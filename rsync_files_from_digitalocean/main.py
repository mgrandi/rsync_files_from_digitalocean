import argparse
import sys
import logging

import logging_tree

from rsync_files_from_digitalocean import utils
from rsync_files_from_digitalocean import application


def main():

    parser = argparse.ArgumentParser(
        description="run rsync on a subset of digital ocean serverse",
        epilog="Copyright 2021-09-02 - Mark Grandi",
        fromfile_prefix_chars='@')

    parser.add_argument("--log-to-file-path",
        dest="log_to_file_path",
        type=utils.isFileType(False),
        help="log to the specified file")

    parser.add_argument("--verbose",
        action="store_true",
        help="Increase logging verbosity")

    parser.add_argument("--no-stdout",
        dest="no_stdout",
        action="store_true",
        help="if true, will not log to stdout" )

    parser.add_argument("--dry-run",
        action="store_true",
        dest="dry_run",
        help="if specified, don't actually perform any action")


    ###########################################

    parser.add_argument("--digital-ocean-api-key",
        dest="digital_ocean_api_key",
        required=True,
        help="the DigitalOcean API key")

    parser.add_argument("--droplet-name-regex",
        dest="droplet_name_regex",
        type=utils.isRegexType,
        help="a regular expression to check the droplet names against, "
            + "if the name matches, we will download files from this droplet")

    parser.add_argument("--rsync-binary",
        dest="rsync_binary",
        required=True,
        type=utils.isFileType(strict=False),
        help="path to the rsync binary")

    parser.add_argument("--rsync-username",
        dest="rsync_username",
        required=True,
        type=str,
        help="rsync ssh username")

    parser.add_argument("--rsync-filter",
        dest="rsync_filter",
        type=str,
        action="append",
        help="a filter to provide to rsync, can be specified multiple times")

    parser.add_argument("--remove-source-files",
        dest="remove_source_files",
        action="store_true",
        help="if specified, we will remove the source files when running rsync")

    parser.add_argument("--droplet-source-folder",
        dest="droplet_source_folder",
        required=True,
        type=str,
        help="the folder on the remote side that we will be rsyncing from")

    parser.add_argument("--local-destination-folder",
        dest="local_destination_folder",
        required=True,
        type=utils.isFileType(False),
        help="the local folder to store the files in")


    try:

        # set up logging stuff
        logging.captureWarnings(True) # capture warnings with the logging infrastructure
        root_logger = logging.getLogger()
        logging_formatter = utils.ArrowLoggingFormatter("%(asctime)s %(threadName)-10s %(name)-20s %(levelname)-8s: %(message)s")

        parsed_args = parser.parse_args()

        if parsed_args.log_to_file_path:

            file_handler = logging.FileHandler(parsed_args.log_to_file_path, encoding="utf-8")
            file_handler.setFormatter(logging_formatter)
            root_logger.addHandler(file_handler)

        if not parsed_args.no_stdout:
            logging_handler = logging.StreamHandler(sys.stdout)
            logging_handler.setFormatter(logging_formatter)
            root_logger.addHandler(logging_handler)


        # set logging level based on arguments
        if parsed_args.verbose:
            root_logger.setLevel("DEBUG")
        else:
            root_logger.setLevel("INFO")

        root_logger.debug("Parsed arguments: %s", parsed_args)
        root_logger.debug("Logger hierarchy:\n%s", logging_tree.format.build_description(node=None))

        # #####################################
        # actually run the application
        # #####################################

        app = application.Application(parsed_args)

        app.run()


        root_logger.info("Done!")

    except Exception as e:
        root_logger.exception("Something went wrong!")
        sys.exit(1)

