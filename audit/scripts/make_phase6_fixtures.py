#!/usr/bin/env python3
"""Phase 6 fixtures for the OpenMontage Kaggle T4 audit (deterministic)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "audit/config"
CFG.mkdir(parents=True, exist_ok=True)

SCRIPT = """The James Webb Space Telescope observes the universe in infrared light. Its primary mirror is made of eighteen hexagonal segments coated with gold, and it orbits the Sun at the second Lagrange point, about 1.5 × 10^8 kilometers from Earth. The telescope studies the atmospheres of exoplanets with spectroscopy, splitting starlight into a spectrum so that astronomers can identify molecules such as water vapor, carbon dioxide, and methane. When an exoplanet passes in front of its star, a small fraction of the starlight passes through the planet's atmosphere, and the absorption lines in that light reveal the composition of the air. This technique is called transmission spectroscopy, and it has transformed our understanding of worlds beyond the solar system.

The mitochondrion is often called the powerhouse of the cell, but that phrase is only a rough summary. Mitochondria are double-membrane organelles with an outer membrane, an inner membrane folded into cristae, and a matrix that contains enzymes, mitochondrial DNA, and ribosomes. They carry out aerobic respiration, converting glucose and oxygen into adenosine triphosphate, or ATP, while releasing carbon dioxide and water. A single human cell may contain hundreds of mitochondria, and the number varies with the cell's energy demand. Mitochondria also participate in programmed cell death, calcium signaling, and the production of heat. The mitochondrion is inherited mainly from the mother in humans, which is why mitochondrial DNA is a useful tool for tracing maternal lineages.

Photosynthesis is the process by which plants, algae, and some bacteria convert light energy into chemical energy. In plants, chloroplasts contain the green pigment chlorophyll, which absorbs red and blue light and reflects green light. The light-dependent reactions take place in the thylakoid membranes and produce ATP and NADPH, while the Calvin cycle takes place in the stroma and fixes carbon dioxide into sugars. The overall equation is six molecules of carbon dioxide plus six molecules of water, driven by light, producing one molecule of glucose and six molecules of oxygen. Photosynthesis is responsible for most of the oxygen in Earth's atmosphere and for nearly all of the energy that flows through the biosphere.

On Earth, the acceleration due to gravity is approximately 9.81 meters per second squared at sea level, although it varies slightly with latitude and altitude. At the surface, a falling object in a vacuum accelerates uniformly, and its speed increases by about 9.81 meters per second every second. The value is not a universal constant in the way that 3.0 × 10^8 meters per second, the speed of light in a vacuum, is a constant. The speed of light is exactly 299,792,458 meters per second by definition, and it is the same for all observers regardless of their motion. This invariance is one of the foundations of Einstein's theory of special relativity.

The human body maintains a core temperature of about 37 degrees Celsius, which is 98.6 degrees Fahrenheit. This temperature is regulated by the hypothalamus, which acts as a thermostat. When the body is too warm, blood vessels in the skin dilate and sweat glands release moisture, and evaporation removes heat. When the body is too cold, blood vessels constrict, shivering generates heat, and metabolic rate increases. The normal range is not a single number: healthy body temperature varies across the day, across individuals, and with activity, and a temperature of 37 degrees Celsius is only a convenient average.

Homo sapiens is the only surviving species of the genus Homo. Our species evolved in Africa over the last several hundred thousand years and later spread across the globe. Escherichia coli is a rod-shaped bacterium that lives in the intestines of humans and other animals. Most strains are harmless, and some are used in biotechnology to produce insulin and other proteins. Escherichia coli is a model organism in molecular biology because it grows quickly and its genome is easy to manipulate. The two organisms could not be more different in size and complexity, yet both are described by the same basic chemistry of DNA, RNA, proteins, and metabolism.

Gravitational waves are ripples in spacetime produced by accelerating masses, especially compact objects such as black holes and neutron stars. The Laser Interferometer Gravitational-Wave Observatory, or LIGO, uses two perpendicular arms, each four kilometers long, with mirrors at the ends. A passing gravitational wave changes the length of the arms by a tiny fraction of the diameter of a proton, and the resulting interference pattern reveals the wave. The first direct detection, announced in 2016, came from the merger of two black holes more than a billion light-years away. Since then, dozens of events have been observed, and gravitational-wave astronomy has become a new way to study the universe.

A nebula is a cloud of gas and dust in space. Some nebulae are regions of active star formation, where gravity pulls material into dense cores that eventually ignite as stars. Others are remnants of dying stars, such as planetary nebulae and supernova remnants. The Orion Nebula, about 1,344 light-years away, is one of the brightest and most studied star-forming regions. Inside it, young stars heat the surrounding gas, causing it to glow. The James Webb Space Telescope can see through much of the dust that obscures visible light, revealing structures that were previously hidden.

Atoms are the smallest units of an element that retain its chemical properties. An atom consists of a nucleus containing protons and neutrons, surrounded by electrons. The number of protons determines the element, and the number of neutrons determines the isotope. For example, carbon has six protons, but carbon-12 has six neutrons while carbon-14 has eight. Molecules are formed when atoms share or transfer electrons. Water is a molecule made of two hydrogen atoms and one oxygen atom, and its bent shape gives it properties that are essential for life, including its ability to dissolve many substances and to moderate temperature.

Enzymes are proteins that act as catalysts, speeding up chemical reactions without being consumed. Each enzyme has an active site whose shape is complementary to its substrate, and the binding of substrate to enzyme lowers the activation energy of the reaction. Enzymes are highly specific: lactase breaks down lactose, amylase breaks down starch, and DNA polymerase builds new DNA strands. Without enzymes, the reactions of metabolism would proceed far too slowly to sustain life. Enzymes are affected by temperature and pH, and extreme conditions can denature them, changing the shape of the active site and stopping the reaction.

The scientific method is a cycle of observation, hypothesis, prediction, experiment, and revision. A hypothesis must be testable and falsifiable, and an experiment must be designed to distinguish between competing explanations. Results are reported with their uncertainties, and independent replication is the strongest test of a claim. Science is not a collection of fixed facts; it is a process for reducing uncertainty. When new evidence contradicts an established idea, the idea must be revised or replaced. This willingness to change is a strength, not a weakness, and it is why science has produced such reliable knowledge about the natural world.

The history of science is full of examples of instruments that opened new windows. Galileo's telescope revealed moons around Jupiter and phases of Venus. Leeuwenhoek's microscope revealed microorganisms. The particle accelerator revealed the structure of the atomic nucleus. The James Webb Space Telescope is the latest in this tradition, and its images of distant galaxies, star-forming regions, and exoplanet atmospheres are already reshaping our understanding of the universe. Yet the instrument is only as good as the questions we ask of it. Spectroscopy, photometry, and careful modeling turn photons into evidence, and evidence into knowledge.

Measurement is the bridge between a model and a claim. A thermometer, a spectrometer, and a gravitational-wave interferometer are all instruments that convert a physical quantity into a number, and each number carries an uncertainty. Scientists report the uncertainty because a measurement without an error bar is incomplete. They also report the method, the instrument, the calibration, and the conditions, because a result that cannot be reproduced is not yet knowledge. This is why the same quantity may be measured in different ways, and why independent measurements are so valuable. When two methods agree within their uncertainties, confidence grows; when they disagree, the disagreement itself becomes the subject of investigation.

In summary, the same physical laws govern the interior of a cell, the atmosphere of a distant exoplanet, and the propagation of gravitational waves across the universe. The mitochondrion, the chloroplast, the enzyme, and the atom are all part of one continuous story, written in the language of physics and chemistry. The James Webb Space Telescope, the Laser Interferometer Gravitational-Wave Observatory, and the microscope are different instruments built to read that story at different scales. Science advances when we build better instruments, ask sharper questions, and remain honest about what the evidence can and cannot show. The universe is vast, and the scientific enterprise is one of the few ways we have to understand it.
"""

TERMS = [
    ("James Webb Space Telescope", ["JWST", "James Webb telescope", "Webb Space Telescope"], "exact phrase, case-insensitive; JWST counts as a variant"),
    ("spectroscopy", ["spectroscopic", "spectroscopist"], "exact word, case-insensitive; do not normalize away"),
    ("exoplanet", ["exoplanets", "exo-planetary"], "exact word or plural"),
    ("gravitational waves", ["gravitational wave", "gravitational-wave"], "exact phrase, hyphen variant allowed"),
    ("mitochondrion", ["mitochondria", "mitochondrial"], "exact word; plural mitochondria accepted"),
    ("Homo sapiens", ["homo sapiens"], "exact Latin binomial, case-insensitive"),
    ("Escherichia coli", ["E. coli", "escherichia coli"], "exact Latin binomial; E. coli accepted"),
    ("photosynthesis", ["photosynthetic", "photosynthesise", "photosynthesize"], "exact word or derived form"),
    ("9.81 meters per second squared", ["9.81 m/s^2", "9.81 m s^-2", "9.81 meters per second per second"], "numeric span with unit variants; record exact token span"),
    ("37 degrees Celsius", ["37 °C", "37 C", "37 degrees C"], "numeric span with unit variants"),
    ("1.5 × 10^8 kilometers", ["1.5e8 kilometers", "150 million kilometers", "1.5 * 10^8 km"], "numeric span; multiplication sign variants"),
    ("3.0 × 10^8 meters per second", ["3.0e8 meters per second", "300 million meters per second", "3.0 * 10^8 m/s"], "numeric span; speed of light context"),
    ("mitochondria", ["mitochondrion"], "plural"),
    ("chloroplast", ["chloroplasts"], "exact word"),
    ("chlorophyll", ["chlorophylls"], "exact word"),
    ("adenosine triphosphate", ["ATP"], "exact phrase or abbreviation"),
    ("deoxyribonucleic acid", ["DNA"], "exact phrase or abbreviation"),
    ("ribonucleic acid", ["RNA"], "exact phrase or abbreviation"),
    ("proton", ["protons"], "exact word"),
    ("neutron", ["neutrons"], "exact word"),
    ("electron", ["electrons"], "exact word"),
    ("enzyme", ["enzymes"], "exact word"),
    ("protein", ["proteins"], "exact word"),
    ("activation energy", ["activation-energy"], "exact phrase"),
    ("Laser Interferometer Gravitational-Wave Observatory", ["LIGO"], "exact phrase or abbreviation"),
    ("Orion Nebula", ["Orion nebula"], "exact proper name"),
    ("light-year", ["lightyears", "light year", "light-years"], "unit"),
    ("absolute zero", ["0 kelvin", "0 K"], "concept/number"),
]


def main() -> None:
    words = SCRIPT.split()
    (CFG / "science_voice_script.txt").write_text(SCRIPT, encoding="utf-8")
    terms_json = {
        "version": "1.0",
        "note": "Exact token spans for term-specific ASR scoring. Do not normalize away term errors.",
        "terms": [
            {"canonical": c, "variants": v, "match_rule": r}
            for c, v, r in TERMS
        ],
    }
    (CFG / "science_terms.json").write_text(json.dumps(terms_json, indent=2, ensure_ascii=False), encoding="utf-8")
    prompts = {
        "version": "1.0",
        "image_prompts": [
            {"id": 1, "seed": 424242, "size": [512, 512], "prompt": "A scientifically accurate, highly detailed educational cutaway illustration of a mitochondrion, showing the outer membrane, inner membrane, cristae, matrix, and ATP synthase complexes, clean studio lighting, clear scientific composition, no labels, no text, no watermark."},
            {"id": 2, "seed": 202607, "size": [512, 512], "prompt": "A scientifically grounded visualization of the James Webb Space Telescope observing a distant exoplanet, realistic engineering details, accurate telescope proportions, deep-space background, educational documentary visual style, no labels, no text, no watermark."},
            {"id": 3, "seed": 271828, "size": [512, 512], "prompt": "A precise scientific visualization of a gravitational-wave observatory with two perpendicular interferometer arms, laser beam paths, mirrors, realistic facility scale, clean explanatory composition, no labels, no text, no watermark."},
        ],
        "video_prompt": "Create a short, scientifically grounded educational documentary shot of a spacecraft approaching a distant exoplanet. Show a slow continuous camera movement, stable object geometry, physically plausible lighting, realistic space-science visual style, no text, no labels, no watermark, no abrupt scene changes.",
        "video_seed": 424242,
        "video_size": [512, 512],
        "video_frames": 49,
    }
    (CFG / "image_video_prompts.json").write_text(json.dumps(prompts, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"script words: {len(words)} (~{len(words)/150:.1f} min at 150 wpm)")
    for name in ("science_voice_script.txt", "science_terms.json", "image_video_prompts.json"):
        p = CFG / name
        print(name, p.stat().st_size, hashlib.sha256(p.read_bytes()).hexdigest()[:16])


if __name__ == "__main__":
    main()