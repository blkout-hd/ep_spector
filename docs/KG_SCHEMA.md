# SPECTOR Knowledge Graph Schema

## Overview

This document defines the knowledge graph schema for the SPECTOR project. The schema is designed for Neo4j but is compatible with other graph databases via Cypher-like query translation.

## Entity Types (Nodes)

### Person
```cypher
(:Person {
  id: UUID,                    # Unique identifier
  name: STRING,                # Full name
  aliases: LIST<STRING>,       # Known aliases
  birth_date: DATE,            # Date of birth (if known)
  death_date: DATE,            # Date of death (if known)
  nationality: STRING,         # Nationality
  occupation: LIST<STRING>,    # Occupations/roles
  gender: STRING,              # Gender identity
  metadata: MAP,               # Additional metadata
  source_documents: LIST<UUID>, # Source document IDs
  confidence_score: FLOAT,     # Entity extraction confidence (0-1)
  created_at: DATETIME,        # When added to KG
  updated_at: DATETIME         # Last update
})
```

### Organization
```cypher
(:Organization {
  id: UUID,
  name: STRING,
  aliases: LIST<STRING>,
  type: STRING,                # Corporation, NGO, Government, etc.
  jurisdiction: STRING,        # Legal jurisdiction
  founded_date: DATE,
  dissolved_date: DATE,
  website: STRING,
  metadata: MAP,
  source_documents: LIST<UUID>,
  confidence_score: FLOAT,
  created_at: DATETIME,
  updated_at: DATETIME
})
```

### Location
```cypher
(:Location {
  id: UUID,
  name: STRING,
  type: STRING,                # Address, Building, City, Country, etc.
  address: STRING,
  city: STRING,
  state: STRING,
  country: STRING,
  coordinates: POINT,          # Lat/Lng
  metadata: MAP,
  source_documents: LIST<UUID>,
  confidence_score: FLOAT,
  created_at: DATETIME,
  updated_at: DATETIME
})
```

### Document
```cypher
(:Document {
  id: UUID,
  title: STRING,
  type: STRING,                # PDF, Email, Memo, Report, etc.
  date: DATE,
  author: STRING,
  recipient: STRING,
  subject: STRING,
  source_url: STRING,
  file_hash: STRING,           # SHA-256 hash
  page_count: INTEGER,
  has_hidden_text: BOOLEAN,    # Whether hidden text was found
  redaction_score: FLOAT,      # Estimated redaction level (0-1)
  suppression_score: FLOAT,    # Semantic suppression delta
  ocr_applied: BOOLEAN,
  language: STRING,
  metadata: MAP,
  created_at: DATETIME,
  updated_at: DATETIME
})
```

### MediaFile
```cypher
(:MediaFile {
  id: UUID,
  filename: STRING,
  type: STRING,                # Image, Video, Audio
  mime_type: STRING,
  size_bytes: INTEGER,
  duration_seconds: FLOAT,     # For audio/video
  dimensions: STRING,          # For images (WxH)
  source_url: STRING,
  file_hash: STRING,
  associated_document: UUID,   # Related document ID
  metadata: MAP,
  created_at: DATETIME,
  updated_at: DATETIME
})
```

### Event
```cypher
(:Event {
  id: UUID,
  name: STRING,
  type: STRING,                # Meeting, Flight, Transaction, etc.
  start_date: DATETIME,
  end_date: DATETIME,
  location: UUID,              # Reference to Location
  description: STRING,
  metadata: MAP,
  source_documents: LIST<UUID>,
  confidence_score: FLOAT,
  created_at: DATETIME,
  updated_at: DATETIME
})
```

### Cluster
```cypher
(:Cluster {
  id: UUID,
  name: STRING,
  type: STRING,                # UMAP, HDBSCAN, Manual
  algorithm: STRING,           # Clustering algorithm used
  dimensions: INTEGER,         # Dimensionality of embedding
  centroid: LIST<FLOAT>,       # Cluster centroid
  member_count: INTEGER,
  metadata: MAP,
  created_at: DATETIME,
  updated_at: DATETIME
})
```

## Relationship Types (Edges)

### Person Relationships
```cypher
(:Person)-[:ASSOCIATED_WITH {
  type: STRING,                # Business, Personal, Family, etc.
  strength: FLOAT,             # Relationship strength (0-1)
  start_date: DATE,
  end_date: DATE,
  source_documents: LIST<UUID>,
  confidence_score: FLOAT
}]->(:Person)

(:Person)-[:EMPLOYED_BY {
  role: STRING,
  start_date: DATE,
  end_date: DATE,
  source_documents: LIST<UUID>
}]->(:Organization)

(:Person)-[:RESIDED_AT {
  start_date: DATE,
  end_date: DATE,
  type: STRING,                # Primary, Secondary, Temporary
  source_documents: LIST<UUID>
}]->(:Location)

(:Person)-[:ATTENDED_EVENT {
  role: STRING,                # Organizer, Attendee, Speaker
  source_documents: LIST<UUID>
}]->(:Event)
```

### Organization Relationships
```cypher
(:Organization)-[:MERGED_WITH {
  date: DATE,
  type: STRING,                # Merger, Acquisition, Partnership
  source_documents: LIST<UUID>
}]->(:Organization)

(:Organization)-[:HEADQUARTERED_AT {
  start_date: DATE,
  end_date: DATE,
  source_documents: LIST<UUID>
}]->(:Location)

(:Organization)-[:ORGANIZED_EVENT {
  role: STRING,                # Sponsor, Host, Organizer
  source_documents: LIST<UUID>
}]->(:Event)
```

### Document Relationships
```cypher
(:Document)-[:MENTIONS_PERSON {
  mention_count: INTEGER,
  context: STRING,
  sentiment: FLOAT
}]->(:Person)

(:Document)-[:MENTIONS_ORGANIZATION {
  mention_count: INTEGER,
  context: STRING
}]->(:Organization)

(:Document)-[:MENTIONS_LOCATION {
  mention_count: INTEGER,
  context: STRING
}]->(:Location)

(:Document)-[:ABOUT_EVENT {
  relevance: FLOAT
}]->(:Event)

(:Document)-[:HAS_MEDIA {
  type: STRING,                # Attachment, Embedded, Referenced
  filename: STRING
}]->(:MediaFile)

(:Document)-[:SIMILAR_TO {
  similarity_score: FLOAT,     # Cosine similarity
  method: STRING               # TF-IDF, BM25, Embedding
}]->(:Document)

(:Document)-[:REDACTED_FROM {
  redaction_method: STRING,
  recovery_method: STRING,
  recovered_text: STRING
}]->(:Document)
```

### Semantic Relationships
```cypher
(:Document)-[:SEMANTICALLY_ADJACENT {
  distance: FLOAT,             # UMAP/t-SNE distance
  cluster_id: UUID,
  algorithm: STRING            # UMAP, t-SNE
}]->(:Document)

(:Document)-[:IN_CLUSTER {
  membership_strength: FLOAT
}]->(:Cluster)

(:Person)-[:IN_CLUSTER {
  membership_strength: FLOAT
}]->(:Cluster)
```

### Media Relationships
```cypher
(:MediaFile)-[:DEPICTS_PERSON {
  confidence: FLOAT
}]->(:Person)

(:MediaFile)-[:DEPICTS_LOCATION {
  confidence: FLOAT
}]->(:Location)

(:MediaFile)-[:CAPTURED_AT_EVENT {
  confidence: FLOAT
}]->(:Event)
```

## Indexes

```cypher
CREATE INDEX person_name_idx FOR (p:Person) ON (p.name)
CREATE INDEX org_name_idx FOR (o:Organization) ON (o.name)
CREATE INDEX location_name_idx FOR (l:Location) ON (l.name)
CREATE INDEX document_title_idx FOR (d:Document) ON (d.title)
CREATE INDEX document_hash_idx FOR (d:Document) ON (d.file_hash)
CREATE INDEX media_hash_idx FOR (m:MediaFile) ON (m.file_hash)
CREATE INDEX event_date_idx FOR (e:Event) ON (e.start_date)
CREATE INDEX cluster_type_idx FOR (c:Cluster) ON (c.type)
```

## Constraints

```cypher
CREATE CONSTRAINT person_id_unique FOR (p:Person) REQUIRE p.id IS UNIQUE
CREATE CONSTRAINT org_id_unique FOR (o:Organization) REQUIRE o.id IS UNIQUE
CREATE CONSTRAINT location_id_unique FOR (l:Location) REQUIRE l.id IS UNIQUE
CREATE CONSTRAINT document_id_unique FOR (d:Document) REQUIRE d.id IS UNIQUE
CREATE CONSTRAINT media_id_unique FOR (m:MediaFile) REQUIRE m.id IS UNIQUE
CREATE CONSTRAINT event_id_unique FOR (e:Event) REQUIRE e.id IS UNIQUE
CREATE CONSTRAINT cluster_id_unique FOR (c:Cluster) REQUIRE c.id IS UNIQUE
```

## Sample Queries

### Find All Associates of a Person
```cypher
MATCH (p:Person {name: $name})-[:ASSOCIATED_WITH]-(associate:Person)
RETURN associate.name, associate.occupation, 
       relationships(associate).type as relationship_type
ORDER BY associate.name
```

### Find Documents Mentioning Multiple Entities
```cypher
MATCH (d:Document)-[:MENTIONS_PERSON]->(p:Person)
WHERE p.name IN $names
WITH d, count(DISTINCT p) as entity_count
WHERE entity_count >= 2
RETURN d.title, d.date, entity_count
ORDER BY entity_count DESC
```

### Find Semantic Clusters
```cypher
MATCH (d:Document)-[:IN_CLUSTER]->(c:Cluster)
WHERE c.type = 'UMAP'
RETURN c.name, count(d) as doc_count, c.algorithm
ORDER BY doc_count DESC
```

### Find Redaction Suppression Scores
```cypher
MATCH (d:Document)
WHERE d.suppression_score > 0.5
RETURN d.title, d.suppression_score, d.redaction_score
ORDER BY d.suppression_score DESC
LIMIT 100
```

---

**Schema Version:** 1.0.0  
**Last Updated:** 2026-02-19  
**Compatible With:** Neo4j 5.x, LightRAG, AuroraDB
