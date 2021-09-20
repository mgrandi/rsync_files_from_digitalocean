import logging
import pathlib
import subprocess
import re

import digitalocean

from rsync_files_from_digitalocean import model

logger = logging.getLogger(__name__)



class Application:


    def __init__(self, parsed_args):

        self.parsed_args = parsed_args

        self.do_manager = None
        self.do_api_key = self.parsed_args.digital_ocean_api_key
        self.droplet_name_regex_obj = self.parsed_args.droplet_name_regex
        self.should_dry_run = self.parsed_args.dry_run
        self.rsync_options = self._get_rsync_options_from_argparse_namespace(self.parsed_args)

    def _get_rsync_options_from_argparse_namespace(self, parsed_args):

        return model.RsyncOptions(
            rsync_binary_path=parsed_args.rsync_binary,
            rsync_filters=parsed_args.rsync_filter,
            droplet_source_folder=parsed_args.droplet_source_folder,
            local_destination_folder_base_path=parsed_args.local_destination_folder,
            username=parsed_args.rsync_username,
            should_remove_source_files=parsed_args.remove_source_files)

    def create_rsync_command_list(self, rsync_options, droplet, iter_droplet_dest_folder):
        '''
        constructs the rsync command line list that we will pass to `subprocess.run()`

        @param rsync_options - the rsync options
        @param droplet - the droplet we are operating on
        @param iter_droplet_dest_folder - where to save the files to for this specific droplet
        @return a list of arguments to pass to `subprocess.run()`
        '''

        # common rsync arguments
        cmd_list = [
            str(rsync_options.rsync_binary_path),
            # "--progress",
            "--itemize-changes",
            "--recursive",
            "--checksum",
            "--partial",
            "--verbose"
            ]

        # if we are removing source files
        if rsync_options.should_remove_source_files:
            cmd_list.append("--remove-source-files")

        # add any filters
        if rsync_options.rsync_filters:
            for iter_filter_str in rsync_options.rsync_filters:
                filter_arg_list = ["--filter", iter_filter_str]
                cmd_list.extend(filter_arg_list)

        cmd_list.extend([
            "{}@{}:{}".format(rsync_options.username, droplet.ip_address, rsync_options.droplet_source_folder),
            "{}".format(iter_droplet_dest_folder)
        ])

        return cmd_list



    def run(self):


        droplet_list = []

        # get droplet list
        try:
            self.do_manager = digitalocean.Manager(token=self.do_api_key)
            logger.info("created digitalocean.Manager: `%s`", self.do_manager)

            logger.info("Querying for the list of Digital Ocean droplets...")
            droplet_list = self.do_manager.get_all_droplets()

            logger.info("Found `%s` total droplets", len(droplet_list))

        except Exception as e:

            logger.exception("Failed to get the droplet list!")
            raise e

        # for iter_droplet in droplet_list:
        #     rsync_cmd_list =

        # now figure out what droplets we should act on
        matched_droplets = []

        for iter_droplet in droplet_list:

            name = iter_droplet.name

            search_res = self.droplet_name_regex_obj.search(name)

            logger.debug("regex `%s` search result against droplet `%s` 's name: `%s`",
                self.droplet_name_regex_obj, iter_droplet, search_res)

            if search_res:
                logger.debug("droplet `%s` matched", name)
                matched_droplets.append(iter_droplet)

        logger.info("`%s` droplets matched our regex", len(matched_droplets))

        for iter_droplet in matched_droplets:

            dest_folder = self.rsync_options.local_destination_folder_base_path / iter_droplet.name
            dest_folder = dest_folder.resolve()

            logger.info("destination folder: `%s`", dest_folder)

            if not dest_folder.exists():

                if self.should_dry_run:

                    logger.info("DRY RUN: would have attempted to create the folder `%s`", dest_folder)

                else:
                    logger.info("attempting to create folder `%s`", dest_folder)
                    dest_folder.mkdir(exist_ok=True)

            rsync_cmd = self.create_rsync_command_list(self.rsync_options, iter_droplet, dest_folder)

            logger.debug("command for droplet `%s` is `%s`", iter_droplet, rsync_cmd)

            command_result = None

            # list the droplet and what rsync command we would have ran if this is a dry run, and then continue the loop
            # and not actually execute the command
            if self.should_dry_run:
                logger.info("DRY RUN: Would have acted on droplet `%s` with the command `%s`", iter_droplet, rsync_cmd)
                continue

            # we are doing it for real, NOT a dry run
            if self.rsync_options.should_remove_source_files:
                logger.info("*** We are removing source files! ***")


            logger.info("starting rsync command to transfer files from the droplet `%s` to `%s`", iter_droplet.name, dest_folder )
            command_result = subprocess.run(rsync_cmd, capture_output=True)

            if command_result.returncode == 0:

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("rsync command for droplet `%s` succeeded: \n\n`%s`", iter_droplet, command_result.stdout.decode("utf-8"))
                else:
                    logger.info("rsync command for droplet `%s` succeeded", iter_droplet.name)
            else:
                logger.exception("command failed for droplet `%s`, command result: `%s`, stdout: `%s`, stderr: `%s`",
                    iter_droplet, command_result, command_result.stdout, command_result.stderr)

