import os
import re
from pathlib import Path

import fitz
import pandas as pd
import spacy
from flask import Blueprint, current_app, flash, redirect, session, url_for

from lexloop.auth import login_required
from lexloop.db import get_db

bp = Blueprint("process", __name__, url_prefix="/process")


@bp.route("/<filename>", methods=["GET"])
@login_required
def process_file(filename):
    user_id = session.get("user_id")
    if not user_id:
        flash("User not authenticated!")
        return redirect(url_for("auth.login"))

    file_path = os.path.join(current_app.config["UPLOADS"], filename)

    if not os.path.exists(file_path):
        flash("File not found!")
        return redirect(url_for("uploads.upload_file"))

    try:
        doc = fitz.open(file_path)
        if not doc.is_pdf:
            flash("File should have pdf extension!")
            return redirect(url_for("uploads.upload_file"))
    except Exception as e:
        flash(f"Error opening file: {str(e)}")
        return redirect(url_for("uploads.upload_file"))

    try:
        text = ""

        for page in doc:
            text += page.get_text()

        ### PRE-PROCESSING ###
        text = re.sub(r"https?://\S+", "", text)  # removes websites
        text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "", text)  # removes emails
        text = re.sub(r"-\n", "", text)  # removes hyphen before newline
        text = re.sub(r"[:;…()\[\]«»]", "", text)  # removes :;…()\[\]«»
        text = re.sub(r"\d+", "", text)  # removes numbers
        text = text.lower()

        try:
            nlp_fr = spacy.load("fr_core_news_lg")
        except OSError:
            flash("Required language model not found. Please contact the administrator.")
            return redirect(url_for("uploads.upload_file"))

        set_french = set()
        target_pos = ["NOUN", "ADV", "ADJ", "VERB"]
        target_length = 4
        doc = nlp_fr(text)

        french_words_with_pos = []
        french_words_with_gender = []
        french_words_with_number = []

        for token in doc:
            if (
                len(token.text) > target_length
                and token.pos_ in target_pos
                and token.ent_type_ == ""
                and not token.is_stop
            ):
                set_french.add(token.lemma_)
                french_words_with_pos.append((token.lemma_, token.pos_))
                french_words_with_gender.append((token.lemma_, token.morph.get("Gender")))
                french_words_with_number.append((token.lemma_, token.morph.get("Number")))

        list_french = list(set_french)
        if not list_french:
            flash("No suitable French words found in the document.")
            return redirect(url_for("uploads.upload_file"))

        ### TRANSLATION (parquet lookup) ###
        dict_path = Path(__file__).resolve().parent.parent / "dictionaries" / "dict_fr_eng.parquet"
        if not dict_path.exists():
            flash("Dictionary file not found.")
            return redirect(url_for("uploads.upload_file"))
        df = pd.read_parquet(dict_path)
        df["french"] = df["french"].str.strip().str.lower()
        df["english"] = df["english"].str.strip().str.lower()
        lookup = (
            df.drop_duplicates(subset=["french"], keep="first")
            .set_index("french")["english"]
            .to_dict()
        )
        list_dictionary = {
            fr: lookup[fr] for fr in list_french if fr in lookup and fr != lookup[fr]
        }

        ### POST-PROCESSING ###
        try:
            nlp_en = spacy.load("en_core_web_sm")
        except OSError:
            flash("Required English language model not found. Please contact the administrator.")
            return redirect(url_for("uploads.upload_file"))

        french_pos_dict = {}
        for word, pos in french_words_with_pos:
            if word not in french_pos_dict:
                french_pos_dict[word] = []
            if pos not in french_pos_dict[word]:
                french_pos_dict[word].append(pos)

        french_gender_dict = {}
        for word, gender in french_words_with_gender:
            if gender:
                french_gender_dict[word] = gender

        def get_french_article(word):
            gender = french_gender_dict.get(word)
            if gender and "Masc" in gender:
                return "le"
            elif gender and "Fem" in gender:
                return "la"
            return "le/la"

        pos_map = {"NOUN": "NOUN", "PROPN": "NOUN", "VERB": "VERB", "ADJ": "ADJ", "ADV": "ADV"}

        matching_pos_dictionary = {}

        for french_word, english_word in list_dictionary.items():
            french_pos_list = french_pos_dict.get(french_word, [])

            english_doc = nlp_en(english_word)
            english_pos = english_doc[0].pos_ if len(english_doc) > 0 else "UNKNOWN"
            english_pos_mapped = pos_map.get(english_pos, english_pos)

            if english_pos_mapped in french_pos_list:
                enhanced_french = french_word
                enhanced_english = english_word

                if english_pos_mapped == "NOUN":
                    article = get_french_article(french_word)
                    if french_word[0].lower() in "aeiouhéèêàœ":
                        enhanced_french = f"l'{french_word}"
                    else:
                        enhanced_french = f"{article} {french_word}"
                    enhanced_english = f"the {english_word}"

                elif english_pos_mapped == "VERB":
                    if english_word.endswith("ing"):
                        base_form = english_word[:-3]
                        enhanced_english = f"to {base_form}"
                    else:
                        enhanced_english = f"to {english_word}"

                matching_pos_dictionary[enhanced_french] = enhanced_english

        try:
            db = get_db()

            for french_word, english_word in matching_pos_dictionary.items():
                cursor = db.execute(
                    "SELECT id FROM dictionary WHERE french_word = ?", (french_word,)
                )
                row = cursor.fetchone()

                if row:
                    dictionary_id = row["id"]
                else:
                    cursor = db.execute(
                        """
                        INSERT INTO dictionary (french_word, english_word)
                        VALUES (?, ?)
                    """,
                        (french_word, english_word),
                    )
                    db.commit()
                    dictionary_id = cursor.lastrowid

                db.execute(
                    """
                    INSERT OR IGNORE INTO dashboard (user_id, dictionary_id, status_word, switch_date)
                    VALUES (?, ?, 'new', NULL)
                """,
                    (user_id, dictionary_id),
                )

            db.commit()
            flash("Document processed successfully!")

        except Exception as e:
            db.rollback()
            flash(f"Database error: {str(e)}")
            return redirect(url_for("uploads.upload_file"))

        return redirect(url_for("dashboard.display"))

    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}")
        return redirect(url_for("uploads.upload_file"))
