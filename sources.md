# Data Sources

This project uses data from various sources that are openly licensed or in the
public domain. Below are the sources and their respective information:


## CC Legal Tools

**Description:** A `.txt` file provided by Timid Robot containing all legal
tool paths.

**API documentation link:**
- [`google_custom_search/legal-tool-paths.txt`][tools-paths]: a list of all
  current Creative Commons (CC) legal tool paths
- [`data/prioritized-tool-urls.txt`][prioritized-tool-urls]: a prioritized list
  of all current CC legal tool URLs

**API information:**
- No API key required
- No query limits

[tools-paths]:data/legal-tool-paths.txt
[prioritized-tool-urls]: data/prioritized-tool-urls.txt


## GCS (Google Custom Search) JSON API

**Description:** The Custom Search JSON API allows user-defined detailed query
and access towards related query data using a programmable search engine.

**Admin links:**
- [Programmable Search - All search engines][gcs-admin]
- [APIs & Services – APIs & Services – Google Cloud console][google-api-admin]

**API documentation links:**
- [Custom Search JSON API Reference | Programmable Search Engine | Google
  Developers][google-json]
- [Google API Python Client Library][google-api-python]
  - [Google API Client Library for Python Docs |
    google-api-python-client][google-api-python]
    - _Reference documentation for the core library
      [googleapiclient][googleapiclient]._
      - See: googleapiclient.discovery > build
    - _[Library reference documentation by API][gcs-library-ref]_
      - See Custom Search v1 [cse()][gcs-cse]
- [Method: cse.list | Custom Search JSON API | Google Developers][cse-list]
- [XML API reference appendices][reference-appendix]

**API information:**
- API key required
- Query limit: 100 queries per day
- Data available through JSON format

**Notes:**
- The data from Google Custom Search will only cover 50+ general, most
  significant categories of CC License for data collection quota constraint.
  As an additional note, the order of precedence of license the collected
  data's first column is sorted due to intermediate data analysis progress.

[gcs-admin]: https://programmablesearchengine.google.com/controlpanel/all
[google-api-admin]: https://console.cloud.google.com/apis/dashboard
[google-json]: https://developers.google.com/custom-search/v1/reference/rest
[google-api-python]: https://github.com/googleapis/google-api-python-client
[googleapiclient]: http://googleapis.github.io/google-api-python-client/docs/epy/index.html
[gcs-library-ref]: https://googleapis.github.io/google-api-python-client/docs/dyn/
[gcs-cse]: https://googleapis.github.io/google-api-python-client/docs/dyn/customsearch_v1.cse.html
[cse-list]: https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
[reference-appendix]: https://developers.google.com/custom-search/docs/xml_results_appendices


## GitHub

**Description:** A development platform for hosting and managing code.

**API documentation link:**
- [GitHub REST API v3](https://docs.github.com/en/rest)

**API information:**
- API key not required but recommended by GitHub
- Query limit: 60 requests per hour if unauthenticated,
  5000 requests per hour if authenticated
- Data available through JSON format

## Wikipedia

**Description:** The Wikipedia API allows users to query statistics of pages,
categories, revisions from a public API endpoint. We have included two urls in
the project: The `WIKIPEDIA_BASE_URL` AND `WIKIPEDIA_MATRIX_URL`. The
`WIKIPEDIA_BASE_URL` provides access to articles, categories, and metadata from
the English version of Wikipedia. It runs on the MediaWiki Action API, but this
instance only provides English Wikipedia data. Then the `WIKIPEDIA_MATRIX_URL`
provides access to information of all wikimedia projects including the different
language edition of wikipedia. It runs on the Meta-Wiki API.

**API documentation link:**
[WIKIPEDIA_BASE_URL documentation](https://en.wikipedia.org/w/api.php)
[WIKIPEDIA_BASE_URL reference page](https://www.mediawiki.org/wiki/API:Main_page)
[WIKIPEDIA_MATRIX_URL documentation](https://meta.wikimedia.org/w/api.php)
[WIKIPEDIA_MATRIX_URL reference page](https://www.mediawiki.org/wiki/API:Sitematrix)

**API information:**
- No API key required
- Query limit: It is rate-limited only to prevent abuse
- Data available through XML or JSON format
- No query limits

[ia-search]: https://internetarchive.readthedocs.io/en/stable/internetarchive.html#internetarchive.Search


## MediaWiki Action API

**Description:** _The MediaWiki Action API is a web service that allows access
to some wiki features like authentication, page operations, and search. It can
provide meta information about the wiki and the logged-in user._ ([API:Main
page - MediaWiki](https://www.mediawiki.org/wiki/API:Main_page))

**API documentation link:**
- [MediaWiki Action API](https://www.mediawiki.org/wiki/API:Main_page)

**API information:**
  - No API key required
  - Query limit: depends on user status and request type
  - Data available through XML or JSON format


## The Metropolitan Museum of Art Collection API

**Description:** _The Met’s Open Access datasets are available through our API.
The API (RESTful web service in JSON format) gives access to all of The Met’s
Open Access data and to corresponding high resolution images (JPEG format) that
are in the public domain._ ([The Metropolitan Museum of Art Collection
API](https://metmuseum.github.io/))

**API documentation link:**
- [Latest Updates | The Metropolitan Museum of Art Collection
  API](https://metmuseum.github.io/)

**API information:**
  - No API key required
  - 80 queries per second


## Vimeo API

**Description:** The Vimeo API allows users to perform filtered, advanced
search on Vimeo videos.

**API documentation link:**
- [Getting Started with the Vimeo API](https://developer.vimeo.com/api/start)

**API information:**
  - API key required
  - Query limit: 5000 authenticated requests per day
  - Data available through JSON format


## YouTube Data API

**Description:** An API from YouTube for platform users to upload videos,
adjust video parameters, and obtain search results.

**API documentation link:**
- [Search: list | YouTube Data API | Google
  Developers](https://developers.google.com/youtube/v3/docs/search/list)

**API information:**
  - API key required
  - Query limit: depends on the type and number of requests
  - Data available through JSON format


## EUROPEANA DATA API

**Description:**
The **Europeana Search API** provides access to digital cultural heritage metadata records aggregated from museums, libraries, and archives across Europe.
This project uses the API to fetch aggregated counts of cultural heritage records by data provider, rights statement, and theme.

**Official API Documentation:**
- [Search API Documentation](https://europeana.atlassian.net/wiki/spaces/EF/pages/2385739812/Search+API+Documentation)

**API information:**
- API key required
- Query parameters allow:
  - Full-text searching (`query`)
  - Retrieving metadata facets (`profile=facets`)
  - Filtering by data provider, rights statement, and theme
- Data available through JSON format
- Offset-based pagination
