# -*- coding: utf-8 -*-
"""MTG_jamendo_autotagging_moodtheme Dataset Loader

.. admonition:: Dataset Info
    :class: dropdown

    The MTG Jamendo autotagging mood/theme Dataset is a new open dataset for music auto-tagging. It
    is built using music available at Jamendo under Creative Commons licenses and tags provided by content uploaders. The
    dataset contains 18,486 full audio tracks with 195 tags from mood/theme. It is provided
    five fixed data splits for a better and fair replication.

    The moodtheme tags are:

    action, adventure, advertising, ambiental, background, ballad, calm, children, christmas, commercial, cool,
    corporate, dark, deep, documentary, drama, dramatic, dream, emotional, energetic, epic, fast, film, fun, funny,
    game, groovy, happy, heavy, holiday, hopeful, horror, inspiring, love, meditative, melancholic, mellow, melodic,
    motivational, movie, nature, party, positive, powerful, relaxing, retro, romantic, sad, sexy, slow, soft,
    soundscape, space, sport, summer, trailer, travel, upbeat, uplifting.

    Emotion and theme recognition is a popular task in music information retrieval that is relevant for music search and
    recommendation systems.

    This task involves the prediction of moods and themes conveyed by a music track, given the raw audio. The examples
    of moods and themes are: happy, dark, epic, melodic, love, film, space etc. Each track is tagged with at least one
    tag that serves as a ground-truth.

    Acknowledgments

    This work was funded by the predoctoral grant MDM-2015-0502-17-2 from the Spanish Ministry of Economy and
    Competitiveness linked to the Maria de Maeztu Units of Excellence Programme (MDM-2015-0502).

    This work has received funding from the European Union's Horizon 2020 research and innovation programme under the
    Marie Skłodowska-Curie grant agreement No. 765068 "MIP-Frontiers".

    This work has received funding from the European Union's Horizon 2020 research and innovation programme under
    grant agreement No 688382 "AudioCommons".
"""
import csv
import json
import os
from typing import Optional, Tuple, BinaryIO

import librosa
import numpy as np
from mirdata import download_utils, jams_utils, core, io

BIBTEX = """@conference {bogdanov2019mtg,
    author = "Bogdanov, Dmitry and Won, Minz and Tovstogan, Philip and Porter, Alastair and Serra, Xavier",
    title = "The MTG-Jamendo Dataset for Automatic Music Tagging",
    booktitle = "Machine Learning for Music Discovery Workshop, International Conference on Machine Learning (ICML 2019)",
    year = "2019",
    address = "Long Beach, CA, United States",
    url = "http://hdl.handle.net/10230/42015"
}"""
INDEXES = {
    "default": "1.0",
    "test": "1.0",
    "1.0": core.Index(filename="mtg_jamendo_autotagging_moodtheme_index_1.0.json"),
}
DOWNLOAD_INFO = """
    The audio files can be downloaded following the path described in https://github.com/MTG/mtg-jamendo-dataset#downloading-the-data
    
    To download audio, unpack and validate all tar archives:
    
    .. code-block:: console

          mkdir /path/to/download
          python3 scripts/download/download.py --dataset autotagging_moodtheme --type audio /path/to/download --unpack --remove
    
    Later add the files to a folder into mir_datasets called audio/ with the following structure:
        > mtg_jamendo_autotagging_moodtheme/
            > audios/
                > 00/
                ...
                > 99/
"""
REMOTES = {
    "metadata": download_utils.RemoteFileMetadata(
        filename="metadata.zip",
        url="https://zenodo.org/record/3826813/files/data.zip?download=1",
        checksum="039ce10f267f6e4e9f72837c76d72b2f",
    )
}


class Track(core.Track):
    """MTG_jamendo_autotagging_moodtheme Track class

    Args:
        track_id (str): track id of the track (JAMENDO track id)

    Attributes:
        audio_path (str): Path to the audio file

    Cached Properties:
        artist_id (str): JAMENDO artist id
        album_id (str): JAMENDO album id
        duration (float): track duration
        tags (str): autotagging moodtheme annotations

    """

    def __init__(
        self,
        track_id,
        data_home,
        dataset_name,
        index,
        metadata,
    ):
        super().__init__(
            track_id,
            data_home,
            dataset_name,
            index,
            metadata,
        )

        self.track_id = track_id
        self.audio_path = self.get_path("audio")

    @property
    def audio(self) -> Optional[Tuple[np.ndarray, float]]:
        """The track's audio

        Returns:
            * np.ndarray - audio signal
            * float - sample rate

        """
        return load_audio(self.audio_path)

    @core.cached_property
    def artist_id(self) -> str:
        return self._track_metadata.get("ARTIST_ID")

    @core.cached_property
    def album_id(self) -> str:
        return self._metadata()["metadata"][self.track_id]["ALBUM_ID"]

    @core.cached_property
    def duration(self) -> float:
        return float(self._metadata()["metadata"][self.track_id]["DURATION"])

    @core.cached_property
    def tags(self) -> str:
        return self._metadata()["metadata"][self.track_id]["TAGS"]

    def to_jams(self):
        # Initialize top-level JAMS container
        return jams_utils.jams_converter(
            audio_path=self.audio_path,
            metadata={
                "track_id": self.track_id,
                "artist_id": self.artist_id,
                "album_id": self.album_id,
                "duration": self.duration,
                "tags": self.tags,
            },
        )


def load_audio(fhandle: BinaryIO) -> Tuple[np.ndarray, float]:
    """Load a MTG_jamendo_autotagging_moodtheme audio file.

    Args:
        fhandle (str or file-like): path or file-like object pointing to an audio file

    Returns:
        * np.ndarray - the mono audio signal
        * float - The sample rate of the audio file

    """
    return librosa.load(fhandle, sr=None, mono=False)


@core.docstring_inherit(core.Dataset)
class Dataset(core.Dataset):
    """
    The MTG_jamendo_autotagging_moodtheme dataset
    """

    def __init__(self, data_home=None, version="default"):
        super().__init__(
            data_home,
            version,
            name="mtg_jamendo_autotagging_moodtheme",
            track_class=Track,
            bibtex=BIBTEX,
            download_info=DOWNLOAD_INFO,
            indexes=INDEXES,
            remotes=REMOTES,
            license_info="Creative Commons Attribution NonCommercial Share Alike 4.0 International.",
        )

    @core.cached_property
    def _metadata(self):
        meta_path = os.path.join(self.data_home, "data/autotagging_moodtheme.tsv")
        if not os.path.exists(meta_path):
            raise FileNotFoundError("Metadata not found. Did you run .download()?")

        with open(meta_path, "r") as fhandle:
            reader = csv.reader(fhandle, delimiter="\t")
            # columns are track_id, artist_id, album_id, path, duration, tags
            track_metadata = {
                line[0]: {
                    "ARTIST_ID": line[1],
                    "ALBUM_ID": line[2],
                    "PATH": line[3],
                    "DURATION": line[4],
                    "TAGS": line[5]
                } 
                for line in reader
                if line[0] != "TRACK_ID"  # skip first line of csv file
            }

        splits = []
        for split_number in range(5):
            split = {}
            path_train = os.path.join(
                self.data_home,
                "data",
                "splits",
                f"split-{split_number}",
                "autotagging_moodtheme-train.tsv",
            )
            with open(path_train, "r") as fhandle:
                reader = csv.reader(fhandle, delimiter="\t")
                track_uris = [line[0] for line in reader]
                split["train"] = track_uris[1:]
            path_validation = os.path.join(
                self.data_home,
                "data",
                "splits",
                f"split-{split_number}",
                "autotagging_moodtheme-validation.tsv",
            )
            with open(path_validation, "r") as fhandle:
                d = list(
                    csv.DictReader(
                        fhandle,
                        delimiter="\t",
                        fieldnames=[
                            "TRACK_ID",
                            "ARTIST_ID",
                            "ALBUM_ID",
                            "PATH",
                            "DURATION",
                            "TAGS",
                        ],
                    )
                )
                split["validation"] = [m["TRACK_ID"] for m in d[1:]]
            path_test = os.path.join(
                self.data_home,
                "data",
                "splits",
                f"split-{split_number}",
                "autotagging_moodtheme-test.tsv",
            )
            with open(path_test, "r") as fhandle:
                d = list(
                    csv.DictReader(
                        fhandle,
                        delimiter="\t",
                        fieldnames=[
                            "TRACK_ID",
                            "ARTIST_ID",
                            "ALBUM_ID",
                            "PATH",
                            "DURATION",
                            "TAGS",
                        ],
                    )
                )
                split["test"] = [m["TRACK_ID"] for m in d[1:]]
            splits[split_number] = split
        meta["splits"] = splits
        return meta

    @core.copy_docs(load_audio)
    def load_audio(self, *args, **kwargs):
        return load_audio(*args, **kwargs)

    def get_track_ids_for_split(self, split_number):
        """Load a MTG_jamendo_autotagging_moodtheme pre-defined split. There are five different train/validation/tests splits.
        Args:
             split_number (int): split to be retrieved from 0 to 4
        Returns:
            * dict: {"train": [...], "validation": [...], "test": [...]} - the train split

        """
        if not (0 <= split_number <= 4):
            raise Exception("Splits avaiables from num 0 to 4")

        return self._metadata["splits"][split_number]