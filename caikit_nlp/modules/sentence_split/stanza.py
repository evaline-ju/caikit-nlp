# Copyright The Caikit Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module contains sentence splitting with stanza for single languages. 
At this time this module is only designed for inference"""
# Standard
from typing import List
import os

# Third Party
from stanza.pipeline.core import DownloadMethod
import stanza

# First Party
from caikit.core.modules import ModuleBase, module
from caikit.core.toolkit import error_handler
import alog

log = alog.use_channel("STZ_SPLIT")
error = error_handler.get(log)

# Local
from ...data_model import Span

TOKENIZE_STR = "tokenize"


@module(
    id="50fdd547-0eef-4407-9964-e278b50e142a",
    name="Stanza sentence split",
    version="0.1.0",
)
class Stanza(ModuleBase):
    # NOTE: no task because
    # 1. Task outputs must be DataBase and this returns List[Span]
    # 2. This module is generally expected to be composed with another module
    # to perform an end-to-end task

    ################################ Constructor #################################################

    def __init__(self, stanza_resources_path, lang="en"):
        super().__init__()
        # For language flexibility, the pipeline could've been instantiated on
        # each inference call, but this would assume all language resources
        # for tokenization are available and would be less efficient for single
        # language use. The default download method would attempt to download
        # resources on first call. To allow this to run in offline manner, we
        # expect the necessary tokenization resource for each language to
        # already be present
        self.stanza_pipeline = stanza.Pipeline(
            lang=lang,
            processors=TOKENIZE_STR,
            dir=stanza_resources_path,
            download_method=DownloadMethod.REUSE_RESOURCES,
        )

    ################################## API functions #############################################

    def run(self, text: str) -> List[Span]:
        """Run sentence split with stanza

        Args:
            text: str
                Input string to be split into sentences

        Returns:
            List[Span]
                Span list corresponding to sentences
        """
        split_doc = self.stanza_pipeline(text)
        span_list = []
        for sentence in split_doc.sentences:
            span_list.append(
                Span(
                    begin=sentence.tokens[0].start_char,
                    end=sentence.tokens[-1].end_char,
                    text=sentence.text,
                )
            )
        return span_list

    # NOTE: no .save, .load is provided here at this time since a .load
    # would either look like .bootstrap or wrapping the stanza_resources_path
    # with an additional config file. Similarly .save does not mean much
    # here since the module is meant to compatible with an existing stanza resource
    @classmethod
    def bootstrap(
        cls, stanza_resources_path: str, lang: str = "en"
    ) -> "StanzaSentenceSplit":
        """Bootstrap a Stanza resource. For this module only the `tokenize`
        dir needs to be present in the resource path for the language.

        To download tokenizer resources for a language:
            `stanza.download('<lang_code', processors='tokenize')`

        Args:
            stanza_resources_path: str
                Path to Stanza resource to be loaded

        Returns:
            StanzaSentenceSplit
                Instance of this class built from the on disk resource
        """
        full_model_path = os.path.abspath(stanza_resources_path)
        error.value_check(
            "<NLP38385969E>",
            os.path.isdir(full_model_path),
            "Model path should be Stanza resource directory",
        )
        # NOTE: Stanza resources can contain multiple languages, but
        # for the purposes of this module to instantiate and reuse a
        # single stanza pipeline, we introspect for a single language
        # If the language is not available, stanza.pipeline will attempt
        # to download the resource, resulting in potential connection errors
        expected_tok_path = os.path.join(full_model_path, lang, TOKENIZE_STR)
        error.value_check(
            "<NLP22128241E>",
            os.path.isdir(expected_tok_path) and os.listdir(expected_tok_path),
            f"No tokenizer resources for expected language: {lang}",
        )
        return cls(
            stanza_resources_path=full_model_path,
            lang=lang,
        )
