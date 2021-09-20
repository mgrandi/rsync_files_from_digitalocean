import pathlib
import typing

import attr


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class RsyncOptions:

    rsync_binary_path:pathlib.Path = attr.ib()
    rsync_filters:typing.Sequence[str] = attr.ib()

    droplet_source_folder:str = attr.ib()
    local_destination_folder_base_path:pathlib.Path = attr.ib()

    username:str = attr.ib()
    should_remove_source_files:bool = attr.ib()
