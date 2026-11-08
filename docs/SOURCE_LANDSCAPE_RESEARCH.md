# Source landscape: structured skill and technical competency evidence

Research snapshot: 2026-11-08

## Scope and decision standard

This review looks for sources that can help decompose professional skills and technical competencies into reusable axes: concept identity, hierarchy, prerequisite/composition, role/task/skill mappings, proficiency, co-occurrence, and demand. It records how the source can actually be acquired, the rights and operational limits on doing so, and what the resulting data can and cannot establish.

“Effort” means time or work actually invested by a person. None of the sources below directly measures individual effort. Occupational experience ranges, curriculum hours, profile/job-posting counts, and popularity are different quantities and must not be relabeled as effort.

Acquisition and reuse are separate questions. A public API, searchable website, or downloadable file does not itself authorize a redistributable corpus. Where a source's API terms are narrower than its file license, this review identifies the route whose reuse terms are documented. No source is marked implemented in the registry without a functioning collector.

## Findings

1. The highest information gain comes from combining independent competency frameworks, not accumulating more job-posting vocabularies. ESCO and O*NET give broad occupational context; NICE, DigComp, and CS2023 contribute explicit task, skill, learning-outcome, or proficiency structure from different institutions and purposes.
2. Stack Overflow's tag dump/API and Developer Survey are complementary but not independent. The dump/API describe questions and tag co-occurrence; the survey captures self-reported use, aspiration, learning, and work context. The dump's old Archive.org route is not a safe assumption for current acquisition: Stack Overflow announced that quarterly dumps are hosted in-house and available through a member profile.
3. Package registries and official documentation contain strong technical composition evidence: declared dependencies, feature flags, TOC nesting, API symbols, and cross-references. Those edges describe software artifacts and publisher-authored documentation. They are not direct evidence that a person possesses a skill.
4. LinkedIn, Indeed, and Dice are attractive market sources but lack a verified public, reusable taxonomy feed for this purpose. Indeed's developer agreement expressly restricts database building and competitive/republishing uses. LinkedIn access is application-approved and scope-bound. Dice terms prohibit automated site retrieval and mining. These are blocked leads pending written terms or a specific licensed export.
5. Lightcast has a detailed, evolving skill vocabulary and relationship model, but current API access is approval/contract based and the free access scope excludes some cross-dataset relationships and high-volume use. Its underlying evidence is substantially job-posting/profile-derived, so it should be compared as a market-model output rather than counted as independent confirmation.
6. To prevent false precision, every integration should preserve source version, retrieval date, exact endpoint/file, declared license, source-native identifiers, and the type of evidence represented. Crosswalks are mappings, not new independent observations.

## Ranked next five integrations

Scoring is a provisional ordinal planning aid, not measured probability. Each factor is 1–5. Information gain is weighted twice because the project needs new axes, not merely cheap volume. Implementation cost is scored with 1 = low and 5 = high; the formula rewards lower cost:

**Priority = (2 × information gain + source independence + reproducibility + (6 − implementation cost)) / 5**

Source independence is about the evidence origin, not whether the formats differ. A mapping copied from another framework receives no extra independence credit.

| Rank | Integration | Information gain | Independence | Reproducibility | Cost | Score | Why now |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | ESCO | 5 | 5 | 5 | 2 | 4.8 | Broad multilingual occupation-to-skill/knowledge graph; free versioned machine-readable downloads and stable concept URIs. |
| 2 | O*NET | 5 | 5 | 5 | 2 | 4.8 | Broad U.S. occupation, task, skill, work-context, and rating structure with quarterly downloadable releases under a mostly CC BY 4.0 database license. |
| 3 | NICE Framework Components | 4 | 5 | 5 | 1 | 4.6 | Cheap reproducible JSON/XLSX and unusually explicit cybersecurity role, competency-area, task, knowledge, and skill structure. Treat partial role-to-TKS mappings as missing data. |
| 4 | DigComp 3.0 | 4 | 4 | 5 | 1 | 4.4 | Open, structured competence statements, learning outcomes, proficiency levels, and K/S/attitude distinctions. Broad digital competence rather than an occupational technology catalog. |
| 5 | CS2023 | 5 | 5 | 3 | 4 | 4.0 | Independent expert curriculum, knowledge units, learning outcomes, and instructional core hours add a curricular axis absent from labor taxonomies. Extraction and redistribution rights make the cost high. |

The two 4.0-ranked options after these are the Stack Overflow Developer Survey and SFIA. The survey is easy to acquire under ODbL but shares publisher and audience with Stack Overflow Q&A. SFIA has direct professional relevance and RDF/Excel files, but all use requires a license, with terms and price to be confirmed. The first technical-composition integration should then be one bounded package ecosystem, likely npm metadata replication or a smaller PyPI project/classifier slice. It is not a substitute for a skills taxonomy.

### Score notes and tradeoffs

- ESCO and O*NET are complementary, not interchangeable: ESCO is multilingual and European, while O*NET is U.S.-focused and unusually rich in occupational ratings, task statements, work context, and detailed work activities.
- NICE scores highly on cost and independence but is cybersecurity-specific. It should not be generalized to all software work.
- DigComp is a competence framework for citizens and lifelong learning. Its hierarchy and proficiency statements can supply reusable decomposition patterns, but occupational mapping requires a separate step.
- CS2023 is fifth despite its extraction cost because core instructional hours and curricular knowledge units provide an independent structural lens. Its hours are instructional allocation, not individual learning effort.
- Package registries likely have high marginal information gain for composition and dependency axes, but they are broad, noisy, and large. Scope one ecosystem and measure data volume before committing to a full replication.
- Lightcast and other job-market aggregators may improve market coverage, but they are neither low-cost nor independent of job/profile text.

## Source assessments

### Stack Overflow and Stack Exchange

#### Tag API and question dump

The Stack Exchange API exposes tag lists and tag metadata as well as endpoints for synonyms, related tags, and tag wikis. The related-tags result is derived from tag pairings in questions; it is a co-occurrence statistic, not a semantic parent-child relation. API limits are documented: default daily quota, per-IP request-rate ceiling, and backoff behavior. This makes the API useful for smoke checks and incremental/small evidence, not for reconstructing the full question hypergraph. See the [API documentation](https://api.stackexchange.com/docs), [related tags endpoint](https://api.stackexchange.com/docs/related-tags), [tag endpoint](https://api.stackexchange.com/docs/tags), and [API throttling guidance](https://api.stackexchange.com/docs/throttle).

Stack Exchange content has historically been published through periodic data dumps, but route and access changed. Stack Overflow's [October 2024 community-product update](https://stackoverflow.blog/2024/10/03/community-product-update-knowledge-as-a-service/) says the quarterly dumps moved in-house and are accessed through each site's user profile. That announcement does not fully document a stable anonymous bulk endpoint, authentication flow, retention, or exact cadence. Archive.org remains a useful historical mirror but should not be treated as the current official acquisition path. Before an acquisition tranche, verify the live route and rights directly. User contributions are licensed under versioned CC BY-SA terms; see [Stack Overflow licensing](https://stackoverflow.com/help/licensing). API use is also subject to the separate [Stack Exchange API terms](https://stackoverflow.com/legal/api-terms-of-use).

The best data semantics remain: tag identities and synonyms; question-level unordered tag sets; answer/question text only where separately licensed and needed; and source-native counts/timestamps. Keep full hyperedges before deriving pair or 3–5 tag summaries. Related-tag API output is a convenient view over the same question corpus, so it is not an independent validation set.

#### Developer Survey

The annual survey is a distinct instrument with a public [results and files page](https://survey.stackoverflow.co/) and [methodology](https://survey.stackoverflow.co/2026/methodology). The 2026 site exposes chart data as structured JSON and identifies each chart's ODbL 1.0 license; anonymized response files are distributed through the survey results page and official survey repository. It covers technologies used and desired, roles, experience, learning, work context, and attitudes. It can support co-occurrence by respondent and subgroup, with respondent counts and survey-year identity.

This is a stronger evidence source for self-reported familiarity and aspiration than a Q&A tag count, but it remains self-report and selection-biased toward people reached through Stack Overflow channels. It is not a performance test, verified competency measure, or hours-worked dataset. The survey and Q&A corpus share publisher and audience, so treat them as related evidence. Preserve raw response values and question wording; do not harmonize away changes between annual instruments. Review [survey license information](https://questions.survey.stackoverflow.co/) and retain the ODbL obligations.

#### Mirrors and derived views

BigQuery public datasets and Snowflake marketplace listings are alternate access/distribution channels for Stack Exchange data. They generally repackage the same underlying source rather than supply independent evidence. Data Explorer is useful for exploratory SQL, but its query-result constraints and underlying shared corpus make it a poor canonical ingestion path. Use these routes for discovery or backup, not as separate corroborating sources.

### Wikidata

Wikidata is already implemented as an identity/context layer. The [official data-access page](https://www.wikidata.org/wiki/Help:Data_access) documents public APIs and database dumps; structured Wikidata content is CC0. Items have QIDs, properties, aliases, claims, qualifiers, references, and external identifiers. The [query service documentation](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual) describes query-service limitations, including throttling and temporary blocks.

Its strongest contribution is concept disambiguation: technology names, aliases, classes, platforms, products, programming languages, and ecosystem relations. It is a community knowledge graph, not a maintained professional competency ontology. Many claims import or map information from other publishers. A Wikidata link to ESCO, O*NET, a software vendor, or a third-party taxonomy must be preserved as an identity mapping, not counted as independent evidence that the mapped concept is true or equivalent. Snapshot dumps are preferable to repeatable SPARQL queries for a corpus baseline.

### Occupational and market skill sources

#### ESCO

The European Commission's [download page](https://esco.ec.europa.eu/en/use-esco/download) provides free versioned datasets in RDF, Turtle, ODS, CSV, XML, and JSON-LD, in 28 languages. ESCO's [FAQ and reuse conditions](https://esco.ec.europa.eu/en/about-esco/faq) allow use and adaptation for any purpose with attribution and clear disclosure of modifications. Current at research time: v1.2.1, last updated 2025-12-10.

ESCO distinguishes occupation concepts from skill/competence and knowledge concepts. It includes preferred/nonpreferred terms, multilingual labels, descriptions, occupation profiles, and mappings to ISCO-08. Concept URIs provide stable identity; download structure links language-specific labels to language-independent relations. This offers a real concept graph: broader/narrower relations and occupation-to-skill/knowledge relations. Pin the exact download release and language set. The web and local APIs use the ESCO OWL data model, but the download page warns that the existing local API is for reference and will be replaced; bulk files are the more reproducible starting point. Current future release cadence is not guaranteed.

Independence is relatively high as an institutional, stakeholder-developed European classification. Some ESCO concepts or mappings connect to other frameworks, including the e-CF and DigComp; mapped rows should not be double-counted as independent corroboration. ESCO classifies occupational relevance, not an individual's competence or effort.

#### O*NET

The [O*NET Resource Center](https://www.onetcenter.org/database.html) currently publishes database 31.0 in CSV, Excel, JSON, SQL, and RDF and describes quarterly updates, with a primary release in Q3. The downloadable files are the recommended snapshot route. O*NET Web Services offer current data but require registration/API approval; published API limits and service terms differ from the database download license. Most database content is CC BY 4.0, but [license exceptions](https://www.onetcenter.org/license_agreements.html) apply to some content. Check the selected tables rather than assigning one blanket license to every file.

The O*NET-SOC occupation taxonomy covers U.S. work and organizes skills, knowledge, abilities, tasks, detailed work activities, work context, interests, work styles, education, training, and experience. Tables contain occupation-by-element ratings, including importance, level, frequency, and relevance where defined. Stable occupation, content-model element, scale, and task IDs support reconciliation between releases. This makes O*NET a dense source for task/competency composition and occupational context.

Ratings describe the importance or level of an element for an occupation; they are not ratings of a named person's proficiency. Education and experience fields are occupational descriptors, not effort totals. O*NET is independent evidence from ESCO, but both are designed to describe labor-market occupations and can share external frameworks or concepts.

#### NICE Framework Components

NIST publishes [NICE Framework Components](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-current-versions) as JSON and XLSX, separately from the framework's SP 800-181 prose. The change log lists version 2.2.0 on 2026-04-28, while the current-version landing page still displays an inconsistent 2025 date. Use the change log for the release date and retain the inconsistency as source metadata.

Components include work-role categories, work roles, competency areas, and task, knowledge, and skill statements. Work roles and competencies have source IDs; relations connect roles/categories and, where supplied, work roles to tasks, knowledge, and skills. NIST's FAQ warns that these task/knowledge/skill alignments are not complete for every work role. The framework is cybersecurity-specific, versioned, free to download, and exceptionally convenient to snapshot. Verify the precise NIST reuse notice for any data copied into a redistributed product.

NICE supplies strong task and competency structure, but no universal proficiency score and no evidence of individual effort. Its independent institutional origin makes it a good contrast to occupational labor surveys.

#### DigComp 3.0

The JRC [DigComp 3.0 resources](https://joint-research-centre.ec.europa.eu/scientific-activities/key-competences-lifelong-learning/digital-competence-framework-digcomp/digcomp-30-resources_en) include a spreadsheet and structured JSON data alongside PDF/editable material. The 2025 fifth edition is released under CC BY 4.0 with attribution, change, and non-endorsement conditions. It has five competence areas, 21 competences, proficiency levels, competence statements, learning outcomes, and glossary entries. Learning outcomes distinguish knowledge, skills, and attitudes.

The framework is for citizen and lifelong-learning digital competence, not specifically for software jobs. That breadth can provide reusable decomposition axes and proficiency descriptors, but mapping to occupational roles requires separate evidence. The JRC publishes an errata list and says the published materials remain unchanged; therefore pin the original downloaded files and store the applicable errata as a separate overlay. The DigComp-to-ESCO work is a mapping project, not independent validation. No fixed future release schedule or API was found.

#### SFIA and European e-CF

[SFIA 9 documentation](https://sfia-online.org/en/sfia-9/documentation) includes PDF, Excel, and RDF Turtle files with skills, responsibility levels, generic attributes, and behavioral factors. This is directly relevant to professional digital work. SFIA also publishes prior editions, allowing version comparisons. However, its [license page](https://sfia-online.org/en/about-sfia/licensing-sfia/using-and-licensing-sfia) says SFIA use requires a license. Free browsing or downloadable files do not mean the extracted dataset is open for redistribution. Obtain the terms, price, version-change process, and data-retention permission before prioritizing a collector.

The European e-Competence Framework is a standards-based ICT-professional competency model. ESCO's [overview](https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/european-e-competence-framework-e-cf) reports 40 competencies; descriptions of EN 16234-1:2019 report 41. The difference appears edition/inventory-sensitive and should not be resolved by assuming one number: preserve the standard edition and exact source list. Public summaries show five e-competence proficiency levels and key knowledge/skill examples, while the normative standard is sold through standards bodies. No authoritative free bulk machine-readable acquisition route or general redistribution license was established. The e-CF is a promising independent comparison framework, but its licensing/acquisition gate keeps it behind open sources.

#### LinkedIn, Indeed, Dice, and Lightcast

LinkedIn has no documented public bulk Skills taxonomy or general-purpose skill endpoint established by this review. Its [API access guidance](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access) says applications must be authorized and authenticated, and access is permission/scope-based; [API terms](https://www.linkedin.com/legal/l/api-terms-of-use) govern content handling and storage. This does not prove no private or partner data product exists. It does mean no reproducible public collector path was verified. Profile skill endorsements and job skills would also be proprietary, platform-specific evidence. Keep blocked until LinkedIn provides scope, cost, retention, and redistribution terms in writing.

Indeed's [developer agreement](https://docs.indeed.com/legal-terms/developer-agreement-third-party) limits API use to an approved integration and restricts database creation/permanent copies, redistribution without written consent, competitive analysis, and competing-product uses. Partner APIs therefore do not establish permission for a standalone reusable skills corpus. No public taxonomy export was found. Keep blocked.

Dice's public [terms](https://www.dice.com/about/terms-and-conditions) prohibit automated retrieval, data mining, and reproduction of site structure/content. The site describes proprietary technology skill/job matching but no public machine-readable taxonomy export was found. Do not crawl it. Keep blocked unless a separately documented API/export and reuse grant appears.

Lightcast is the strongest market-taxonomy lead. Its [skills taxonomy page](https://lightcast.io/taxonomies/skills-taxonomy) describes over 34,000 concepts organized into category, subcategory, and skill tiers, with unique IDs and definitions. Its [access documentation](https://docs.lightcast.io/lightcast-api/docs/api-access) says public-good access is free but approval-based; commercial or production use requires a commercial license. The free API scope includes taxonomy metadata but limits extraction to 50 requests per month and excludes other taxonomies and cross-dataset relationships. A complete downloadable spreadsheet was not offered in the reviewed docs. The taxonomy's [methodology](https://kb.lightcast.io/en/articles/7216059-lightcast-skills-taxonomy-methodology-and-skills-v10) says it is built from hundreds of millions of postings, resumes, and profiles, updated every four weeks, with current v10 released 2026-10-23. It uses both a defined category hierarchy and dynamic supply/demand relationships.

Lightcast combines taxonomist curation with aggregated market data, making it valuable for demand and market vocabulary but not independent of the labor texts underlying LinkedIn, Indeed, Dice, and other job sources. Its data may map to O*NET, which also does not make those records independent. Clarify API limits, stable IDs, historical snapshots, price, and redistribution before implementation.

### Independent technical taxonomies and curricula

#### CS2023

The [ACM/IEEE-CS/AAAI CS2023 site](https://csed.acm.org/) publishes the report and structured knowledge-area pages. It defines 17 knowledge areas containing knowledge units and topics, identifies CS Core and Knowledge Area Core topics, gives illustrative learning outcomes, and allocates core instructional hours. These axes are valuable because they express what expert curriculum authors think a computing graduate should encounter, independent of job ads or question volume.

Acquisition is through official HTML and report PDFs; no complete public API or machine-readable export was found. Report editions and web page structure must be pinned. The report is copyrighted by its sponsoring organizations; [ACM's permissions terms](https://www.acm.org/publications/policies/copyright-policy) and report notices should be reviewed before redistribution. A research mapping may be possible with limited excerpts or permission, but the repository should not publish a full transformed taxonomy until rights are resolved. Core hours mean curriculum instructional allocation, not time invested by each learner.

#### ACM Computing Classification System

The [ACM CCS 2012 page](https://www.acm.org/publications/class-2012) presents a structured computing subject hierarchy used to index publications. It offers an independent technical vocabulary and stable concept references, but it classifies scholarly subject matter rather than skills, roles, or proficiency. A current official bulk download/API and redistribution terms were not found in this review. The registry therefore marks it blocked pending a reproducible, rights-cleared source file. Individual paper CCS tags are assignments using the scheme, not independent semantic relationships among skills.

#### IEEE Technology Navigator

IEEE's [TechNav FAQ](https://technav.ieee.org/faq/) describes 8,800+ engineering/technology topics derived from the IEEE Thesaurus, an API for searching topics and associated resources, and annual taxonomy updates. API access requires an IEEE-issued key. Topics have a useful hierarchy, while topic-to-publication, standard, course, video, and organization links reveal technical artifact neighborhoods.

The API's visible existence is not enough to justify a corpus. The public TechNav FAQ does not settle API rate limits or bulk rights. IEEE Xplore's separate API terms require approved access and restrict bulk presentation and downstream distribution; those terms cannot automatically be imputed to TechNav, but they demonstrate that IEEE API data access is contract-sensitive. Treat TechNav as blocked pending its own written API and redistribution terms. The taxonomy itself is independent of labor-market evidence, while associated counts and resources are generated from IEEE's own publication collection.

#### Technical documentation structures

Official documentation is a source family, not one uniform dataset. Prefer first-party Git repositories and structural files over HTML scraping:

- [Microsoft Learn documentation repositories](https://github.com/MicrosoftDocs) commonly expose TOC.yml, article frontmatter, API reference symbols, and DocFX build artifacts. Navigation changes with documentation commits; licenses vary by repository and may separate documentation from code.
- [MDN content](https://github.com/mdn/content) and its sidebars encode product and web-platform subject hierarchy. Check the repository's CC BY-SA documentation license and distinguish code-example licenses.
- [Python documentation sources](https://github.com/python/cpython/tree/main/Doc) are authored alongside CPython and built with Sphinx; generated indexes and inventories can identify modules and references. Pin the release and inspect license notices.

Documentation can expose authored domain structure, containment, sequence, and explicit cross-references. It rarely states that a link is a prerequisite. A navigation parent should be modeled as a publisher's information architecture, not a transitive conceptual subsumption edge. A product's own documentation is independent of Stack Overflow questions, but not independent from the vendor's product ontology. Repository commit histories make these sources reproducible if rights and versions are retained.

#### MIT OpenCourseWare and course catalogs

[MIT OpenCourseWare](https://ocw.mit.edu/) exposes course pages and downloadable course materials, often including prerequisites, syllabi, topic/week sequences, assignments, and readings. No complete general-purpose catalog API was found. Course numbers and archived term versions provide usable identities, but per-course and per-asset licensing varies: much material is CC BY-NC-SA 4.0 while some materials are reserved or otherwise restricted. Review each selected course and resource; a site-wide default must not be applied indiscriminately.

Course prerequisities and ordered topic sequences provide curriculum composition, while posted hours or workload estimates are sporadic and not actual personal effort. Instructor selection and course availability create selection bias. The ACM/IEEE-CS/AAAI CS2023 framework is more coherent and machine-readable in concept, but MIT OCW can supply richer implementation-level examples and course artifacts when item licensing permits.

### Package registries

Package registries are not skill ontologies. They contain names, versions, publisher-provided descriptions, keywords/classifiers, manifests, and dependency declarations. They supply technical identity and explicit composition between software artifacts. Registry data is often cross-published and publisher-entered; package dependencies do not imply that one package's users know how to use another. Package download or popularity counts are noisy usage signals, not worker demand or effort. Keep registry metadata rights separate from the licenses of downloadable package artifacts.

- **npm.** The first-party [registry replication API](https://github.com/npm/registry/blob/main/docs/REPLICATE-API.md) documents CouchDB-style replication and a changes feed; [npm terms](https://docs.npmjs.com/policies/open-source-terms/) permit replication of public-registry data through public APIs but prohibit unreasonable request volume and call five million monthly requests clearly unreasonable. Package/version IDs and manifest dependencies form useful composition edges. Keywords and descriptions are publisher supplied. Incremental replication is a better acquisition model than repeated full scans.
- **PyPI.** The official [JSON API](https://docs.pypi.org/api/json/) returns project/release metadata, digests, and Core Metadata; [API policy](https://docs.pypi.org/api/) states there is currently no edge rate limit but discourages thousands of requests in minutes and reserves the right to block irresponsible use. Trove classifiers and keywords are submitted by projects; [classifier documentation](https://pypi.org/classifiers/) describes the controlled values, but assignment is not centrally validated. No general blanket metadata license or complete downloadable snapshot was established.
- **NuGet.** The [V3 registration resource](https://learn.microsoft.com/en-us/nuget/api/registration-base-url-resource) gives package/version metadata and framework-specific dependency groups. The chronological [Catalog resource](https://learn.microsoft.com/en-us/nuget/api/catalog-resource) records pushes, relisting, deprecation, vulnerability changes, and delete events. [Rate-limit documentation](https://learn.microsoft.com/en-us/nuget/api/rate-limits) says V3 search is currently not rate-limited, while other surfaces have quotas and may return 429/403. Package IDs, versions, dependency groups, and event timestamps are strong incremental-ingest anchors.
- **crates.io.** Cargo documents the [sparse and git indexes](https://doc.rust-lang.org/cargo/reference/registry-index.html), which contain versioned package metadata and dependencies; the [crates.io API policy](https://github.com/rust-lang/rfcs/blob/master/text/3463-crates-io-policy-update.md) sets one request per second and asks for an identifying User-Agent. The index is a more suitable bulk source than issuing API calls or downloading crate archives. Metadata includes keywords, categories, dependency features, and package/version IDs; tags remain publisher supplied.
- **Maven Central.** Sonatype documents a [Search REST API](https://central.sonatype.org/search/rest-api-guide/) for coordinates and artifact metadata. POM files may expose group/artifact/version, licenses, dependencies, scope, and optionality. Requests may be rate limited and aggressive use can be blocked; use the published [429 guidance](https://central.sonatype.org/faq/429-error/) and published repository endpoints. There is no standardized skill taxonomy in POM tags, and metadata/artifact rights remain distinct.

A first implementation should be bounded and resumable. npm's replication feed is unusually reproducible for incremental metadata but potentially broad in volume. A PyPI classifier-focused slice may be cheaper for a first experiment, but it will underrepresent skills not expressed in classifier vocabulary. Compare the first snapshot and reconciliation cost before expanding to all registries.

## Cross-source independence and interpretation rules

Use these distinctions in later analysis:

- **Taxonomy**: a source-authorized category, hierarchy, or controlled term system (ESCO, O*NET, NICE, DigComp, SFIA, e-CF, ACM CCS, IEEE).
- **Identity**: stable source ID, aliases, external ID, package coordinate, or URL (Wikidata, ESCO URIs, O*NET IDs, package coordinates).
- **Composition/dependency**: explicitly declared dependency, prerequisite, area/unit/topic membership, or task-to-skill relation (package manifests, course prerequisites, curriculum nesting, selected NICE mappings).
- **Co-occurrence**: terms observed together in a question, respondent, profile, posting, or package manifest. Preserve the unit of observation and do not confuse this with semantic relatedness.
- **Competency/proficiency**: framework statements about expected skill, task, knowledge, or level. These are source-defined standards or models, not direct assessments of an individual.
- **Market demand**: postings, profiles, or employer signals. This is a market observation, affected by duplicated ads, platform coverage, extraction models, and recency.
- **Effort**: only an explicit record of actual time/work invested by a person. None of these sources supplies that at adequate individual granularity.

Where two sources exchange mappings, model the mapping provenance explicitly. For example, ESCO mappings to an e-CF concept do not produce two independent assertions. Wikidata's imported external IDs are identity bridges. Lightcast's mapping to O*NET is a crosswalk. Stack Overflow's related tags, BigQuery public table, and Stack Exchange dump are derivative views of the same underlying community data.

## Open questions to close before collectors

1. Recheck the current Stack Exchange dump acquisition route and its exact access/authentication conditions. Keep the existing acquisition-script work separate from this research branch.
2. For each open data source, save the source-native release identifier, download URL, retrieval timestamp, file hash, source license text/version, and any errata/change log alongside acquired files.
3. Ask SFIA, Lightcast, IEEE TechNav, and any proposed LinkedIn/Indeed/Dice partner contact for written rights covering machine acquisition, retention, transformation, redistribution, and derived statistics. Do not infer rights from a public browser or an API key.
4. For copyrighted curriculum sources, separate private research access from public transformed output. CS2023 and e-CF are high-value but need rights-resolved acquisition.
5. For all “effort” questions, pursue a separate evidence design. Curriculum hours, job experience requirements, popularity, and proficiency levels are not person-level time investment.
6. Before committing to package registry replication, estimate snapshot size, incremental update volume, metadata retention, duplicate handling, and the exact subset needed to answer the meta-axis question.

## Primary-source references

- [Stack Exchange API documentation](https://api.stackexchange.com/docs), [throttling](https://api.stackexchange.com/docs/throttle), [Stack Overflow licensing](https://stackoverflow.com/help/licensing), and [quarterly dump access announcement](https://stackoverflow.blog/2024/10/03/community-product-update-knowledge-as-a-service/).
- [Stack Overflow Developer Survey results](https://survey.stackoverflow.co/), [2026 methodology](https://survey.stackoverflow.co/2026/methodology), and [survey license statement](https://questions.survey.stackoverflow.co/).
- [Wikidata data access](https://www.wikidata.org/wiki/Help:Data_access) and [Wikidata Query Service manual](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual).
- [ESCO downloads](https://esco.ec.europa.eu/en/use-esco/download), [ESCO FAQ/license](https://esco.ec.europa.eu/en/about-esco/faq), and [ESCO version history](https://esco.ec.europa.eu/en/about-esco/what-is-esco).
- [O*NET database](https://www.onetcenter.org/database.html) and [O*NET licenses](https://www.onetcenter.org/license_agreements.html).
- [NICE current component files](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-current-versions) and [NICE change log](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/current-version/change-logs).
- [DigComp 3.0 data and license](https://joint-research-centre.ec.europa.eu/scientific-activities/key-competences-lifelong-learning/digital-competence-framework-digcomp/digcomp-30-resources_en).
- [SFIA 9 files](https://sfia-online.org/en/sfia-9/documentation) and [SFIA licensing](https://sfia-online.org/en/about-sfia/licensing-sfia/using-and-licensing-sfia).
- [ESCO e-CF overview](https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/european-e-competence-framework-e-cf) and [CEN standards distribution policy](https://boss.cen.eu/developingdeliverables/managingwork/pages/pubdistechdel/).
- [CS2023 curriculum site](https://csed.acm.org/) and [ACM copyright/permissions policy](https://www.acm.org/publications/policies/copyright-policy).
- [ACM CCS 2012](https://www.acm.org/publications/class-2012), [IEEE TechNav FAQ](https://technav.ieee.org/faq/), and [IEEE Xplore API terms](https://developer.ieee.org/API_Terms_of_Use2).
- [LinkedIn API access](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access) and [LinkedIn API terms](https://www.linkedin.com/legal/l/api-terms-of-use).
- [Indeed third-party developer agreement](https://docs.indeed.com/legal-terms/developer-agreement-third-party) and [Dice terms](https://www.dice.com/about/terms-and-conditions).
- [Lightcast taxonomy](https://lightcast.io/taxonomies/skills-taxonomy), [API access](https://docs.lightcast.io/lightcast-api/docs/api-access), and [Skills v10 methodology](https://kb.lightcast.io/en/articles/7216059-lightcast-skills-taxonomy-methodology-and-skills-v10).
- [npm replication API](https://github.com/npm/registry/blob/main/docs/REPLICATE-API.md) and [npm terms](https://docs.npmjs.com/policies/open-source-terms/).
- [PyPI JSON API](https://docs.pypi.org/api/json/), [PyPI API policies](https://docs.pypi.org/api/), and [Trove classifiers](https://pypi.org/classifiers/).
- [NuGet registration](https://learn.microsoft.com/en-us/nuget/api/registration-base-url-resource), [NuGet catalog](https://learn.microsoft.com/en-us/nuget/api/catalog-resource), and [NuGet rate limits](https://learn.microsoft.com/en-us/nuget/api/rate-limits).
- [Cargo registry index](https://doc.rust-lang.org/cargo/reference/registry-index.html), [crates.io API policy](https://github.com/rust-lang/rfcs/blob/master/text/3463-crates-io-policy-update.md), [Maven Central REST API](https://central.sonatype.org/search/rest-api-guide/), and [Sonatype 429 guidance](https://central.sonatype.org/faq/429-error/).
- [MicrosoftDocs repositories](https://github.com/MicrosoftDocs), [MDN content repository](https://github.com/mdn/content), [CPython documentation source](https://github.com/python/cpython/tree/main/Doc), and [MIT OpenCourseWare](https://ocw.mit.edu/).
