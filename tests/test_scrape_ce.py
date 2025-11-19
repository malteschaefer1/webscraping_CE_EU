import textwrap

from scrape_ce import GoodPractice, parse_practices


FULL_HTML = textwrap.dedent(
    """
    <div class="node--type-cecon-good-practice">
        <h2><a href="/platform/en/good-practices/example-entry">Circular Cities</a></h2>
        <div class="field-wrapper field field-node--field-cecon-abstract field-name-field-cecon-abstract field-type-text-long field-label-hidden">
            Innovative reuse of construction materials.
        </div>
        <div class="field-wrapper field field-node--field-cecon-organisation-company field-name-field-cecon-organisation-company field-type-link field-label-above">
            <a href="https://example.org">Circular Org</a>
        </div>
        <div class="field-wrapper field field-node--field-cecon-contributor-category field-name-field-cecon-contributor-category field-type-entity-reference field-label-above">
            <a href="/organisation">SME</a>
        </div>
        <div class="field-wrapper field field-node--field-cecon-country field-name-field-cecon-country field-type-country field-label-above">
            <div class="field-item">Belgium</div>
        </div>
        <div class="field-wrapper field field-node--field-cecon-main-language field-name-field-cecon-main-language field-type-entity-reference field-label-above">
            <a href="/language">English</a>
        </div>
        <div class="field-wrapper field field-node--field-cecon-key-area field-name-field-cecon-key-area field-type-entity-reference field-label-above">
            <div class="field-item"><a href="/key-area/waste">Waste</a></div>
            <div class="field-item"><a href="/key-area/recycling">Recycling</a></div>
        </div>
        <div class="field-wrapper field field-node--field-cecon-sector field-name-field-cecon-sector field-type-entity-reference field-label-above">
            <div class="field-item"><a href="/sector/construction">Construction</a></div>
        </div>
        <div class="field-wrapper field field-node--field-cecon-scope field-name-field-cecon-scope field-type-entity-reference field-label-above">
            <div class="field-item"><a href="/scope/national">National</a></div>
            <div class="field-item"><a href="/scope/local">Local</a></div>
        </div>
    </div>
    """
)

MINIMAL_HTML = textwrap.dedent(
    """
    <div class="node--type-cecon-good-practice">
        <h2>Untitled entry</h2>
    </div>
    """
)


def test_parse_practices_extracts_expected_fields():
    practices = parse_practices(FULL_HTML)
    assert len(practices) == 1
    practice = practices[0]
    assert isinstance(practice, GoodPractice)
    assert practice.title == "Circular Cities"
    assert practice.organisation == "Circular Org"
    assert practice.type_of_organisation == "SME"
    assert practice.country == "Belgium"
    assert practice.language == "English"
    assert practice.key_area == "Waste, Recycling"
    assert practice.link.endswith("/platform/en/good-practices/example-entry")


def test_parse_practices_handles_missing_optional_fields():
    practices = parse_practices(MINIMAL_HTML)
    assert len(practices) == 1
    practice = practices[0]
    assert practice.organisation == "N/A"
    assert practice.scope == "N/A"
