# 📊 Confidence Scoring System - Complete Guide

The ZyoniaRAG system includes a sophisticated confidence scoring mechanism that evaluates search results on **4 key dimensions** with a total maximum score of **100 points**. This ensures high-quality, reliable information for neighborhood analysis.

## 🏗️ Score Components Overview

| Component                | Max Points | Purpose                               |
| ------------------------ | ---------- | ------------------------------------- |
| **🏛️ Domain Authority**  | 40         | Website trustworthiness & credibility |
| **🎯 Content Quality**   | 40         | Relevance, depth & data richness      |
| **⚙️ Technical Quality** | 10         | Content enhancement & accessibility   |
| **📅 Recency Estimate**  | 10         | How current/up-to-date the content is |
| **📊 TOTAL**             | **100**    | Overall confidence score              |

---

## 🏛️ Domain Authority (0-40 points)

Measures the trustworthiness and reputation of the source website based on domain patterns and known authority scores.

### Score Ranges:

| Score Range | Source Type           | Examples                                                   |
| ----------- | --------------------- | ---------------------------------------------------------- |
| **35-40**   | Government/Official   | `gov.es`, `madrid.es`, `ine.es`, `policia.es`, `gov.uk`    |
| **30-35**   | Academic/Research     | Universities, `.edu`, `csic.es`, `mit.edu`, `ox.ac.uk`     |
| **25-30**   | Established Media     | BBC, El País, Reuters, The Guardian, La Vanguardia         |
| **20-28**   | Real Estate Platforms | Idealista (28), Fotocasa (27), Numbeo (25), Rightmove (27) |
| **15-25**   | Travel/Review Sites   | TripAdvisor (20), Booking.com (18), Timeout (27)           |
| **10-18**   | Community/Expat Sites | ExpatExchange (22), TheLocal.es (20), Internations (21)    |
| **5-12**    | Personal Blogs        | WordPress (10), Blogspot (8), Medium (12)                  |
| **15**      | Unknown Domains       | Default score for unrecognized domains                     |

### Special Patterns:

- **Educational**: Any domain with `.edu` or `university` gets 33-35 points
- **Government**: Any domain with `.gov` gets 36-38 points
- **Police/Security**: Domains with `police` or `government` get 36 points

---

## 🎯 Content Quality (0-40 points)

Evaluates how well the content matches your search and provides valuable information across 4 dimensions.

### 4 Sub-Components (10 points each):

#### 1. **Neighborhood Specificity (0-10)**

- **Purpose**: Measures if content discusses specific geographic areas
- **Keywords**: "neighborhood", "district", "area", "barrio", "distrito", "zone", "quarter", "sector"
- **Scoring**: **+2 points** per relevant location term (capped at 10)
- **Example**: "The Salamanca district is a neighborhood in the central area" = 6 points

#### 2. **Query Relevance (0-10)**

- **Purpose**: How well content matches your search terms
- **Method**: Counts search words found in title and snippet
- **Scoring**: **+1.5 points** per matched search term (capped at 10)
- **Example**: Search "crime rate Salamanca" finds "crime", "rate", "Salamanca" = 4.5 points

#### 3. **Content Depth (0-10)**

- **Purpose**: Distinguishes between data-driven content vs opinions
- **Quality Indicators**:
  - **High Quality (+3 each)**: "statistics", "data", "research", "study", "survey", "government", "police"
  - **Medium Quality (+2 each)**: "guide", "review", "local", "resident", "experience", "neighborhood"
  - **Low Quality (-1 each)**: "blog", "opinion", "personal", "think", "feel", "maybe"
- **Example**: "Government statistics show crime data" = 6 points

#### 4. **Data Richness (0-10)**

- **Purpose**: Rewards content with quantitative information
- **Patterns Detected**:
  - Percentages: `\d+%`
  - Decimals: `\d+\.\d+`
  - Keywords: "statistics", "data", "rate", "index"
- **Scoring**: **+2 points** per pattern detected (capped at 10)
- **Example**: "Crime rate 2.1% with 15% increase" = 6 points

---

## ⚙️ Technical Quality (0-10 points)

Measures technical aspects and content accessibility.

| Feature                 | Points | Description                                                  |
| ----------------------- | ------ | ------------------------------------------------------------ |
| **Content Enhanced**    | +5     | Successfully scraped additional content from the webpage     |
| **Substantial Content** | +3     | Snippet longer than 100 characters (indicates detailed info) |
| **Valid URL**           | +2     | Working, accessible URL provided (not "No URL")              |

### Example Scoring:

- Enhanced content + long snippet + valid URL = **10/10 points**
- Basic snippet + valid URL = **5/10 points**
- Broken or missing URL = **0-3/10 points**

---

## 📅 Recency Estimate (0-10 points)

Evaluates how current and up-to-date the content appears based on temporal indicators.

| Indicator               | Points | Examples                                 | Detection Method       |
| ----------------------- | ------ | ---------------------------------------- | ---------------------- |
| **Current Year**        | 10     | Contains "2025"                          | Direct year matching   |
| **Previous Year**       | 8      | Contains "2024"                          | Recent year detection  |
| **Recent Updates**      | 6      | "updated", "recent", "latest", "current" | Keyword matching       |
| **No Clear Indicators** | 5      | No temporal clues found                  | Default moderate score |

### Algorithm:

1. **Primary**: Search for current/recent years (2024-2026)
2. **Secondary**: Look for update-related keywords
3. **Fallback**: Assign moderate score if no indicators found

---

## 🎯 Confidence Levels & RAG Weighting

The total score determines the confidence level and RAG system weighting:

| Score Range | Level     | Badge | Description                           | RAG Weight | Use Case                           |
| ----------- | --------- | ----- | ------------------------------------- | ---------- | ---------------------------------- |
| **80-100**  | Very High | 🟢    | Government data, academic research    | 0.8-1.0    | Primary sources for factual claims |
| **65-79**   | High      | 🔵    | Established media, official platforms | 0.65-0.79  | Strong supporting evidence         |
| **50-64**   | Medium    | 🟡    | Decent sources with good content      | 0.5-0.64   | General information, context       |
| **35-49**   | Low       | 🟠    | Personal blogs, older content         | 0.35-0.49  | Background context only            |
| **0-34**    | Very Low  | 🔴    | Unreliable or broken sources          | 0.0-0.34   | Should be filtered out             |

---

## 📋 Example Analysis Breakdown

### Sample Result:

```json
{
  "title": "Salamanca District Safety Report 2025 - Madrid Police",
  "url": "https://policia.es/madrid/salamanca-safety-2025",
  "snippet": "Official crime statistics show Salamanca district has 2.1% crime rate, updated March 2025. Research indicates 85% resident satisfaction with safety measures in the neighborhood area.",
  "content_enhanced": true
}
```

### Scoring Breakdown:

#### 🏛️ Domain Authority: 38/40

- `policia.es` = Government/Police domain = **38 points**

#### 🎯 Content Quality: 32/40

- **Neighborhood Specificity**: "district", "neighborhood", "area" = **6 points**
- **Query Relevance**: "Salamanca", "safety", "crime" matched = **4.5 points**
- **Content Depth**: "Official", "statistics", "research" = **9 points**
- **Data Richness**: "2.1%", "85%", "statistics" = **6 points**
- **Total**: 25.5 → **26 points** (rounded)

#### ⚙️ Technical Quality: 10/10

- Content Enhanced: +5, Substantial content: +3, Valid URL: +2 = **10 points**

#### 📅 Recency Estimate: 10/10

- Contains "2025" and "updated March 2025" = **10 points**

### Final Score:

```
🏛️ Domain Authority:  38/40
🎯 Content Quality:   32/40
⚙️ Technical Quality: 10/10
📅 Recency Estimate:  10/10
─────────────────────────────
📊 TOTAL:            90/100 = 🟢 Very High Confidence
RAG Weight:          0.90
```

---

## 🚀 Implementation Details

### Code Location:

- **Main Module**: `external_enrichment/confidence_scorer.py`
- **Integration**: Used in `searxng_engine.py` when `add_confidence=True`

### Usage in Search:

```python
# Standard mode (includes confidence scoring)
python3 search_neighborhood.py "Salamanca, Madrid" "Is it safe?"

# Fast mode (skips confidence scoring)
python3 search_neighborhood.py "Salamanca, Madrid" "Is it safe?" --fast
```

### Performance Impact:

- **Standard Mode**: +2-3 seconds processing time
- **Fast Mode**: Skipped for better performance
- **Memory**: Minimal overhead (~1-2MB per 10 results)

---

## 🎛️ Configuration Options

### Domain Authority Customization:

Located in `confidence_scorer.py`:

```python
self.authority_scores = {
    'new-domain.com': 25,  # Add custom domain scores
    'trusted-source.es': 35
}
```

### Quality Indicators Tuning:

```python
self.quality_indicators = {
    'high': ['statistics', 'data', 'research'],  # Modify quality keywords
    'medium': ['guide', 'review', 'local'],
    'low': ['blog', 'opinion', 'personal']
}
```

---

## 🔬 Testing & Validation

### Test Command:

```bash
cd external_enrichment
python3 confidence_scorer.py
```

### Expected Output:

```
Confidence Scoring Test Results:
==================================================

Source 1: Madrid Crime Statistics 2024 - Official Police...
Confidence Score: 88/100
Confidence Level: very_high
RAG Weight: 0.88
Domain Authority: 38

Source 2: My Experience Living in Salamanca - Travel Blog...
Confidence Score: 23/100
Confidence Level: very_low
RAG Weight: 0.23
Domain Authority: 10
```

---

## 📈 Benefits for RAG Systems

1. **🎯 Smart Source Weighting**: Higher confidence sources get more influence in AI responses
2. **🔍 Quality Filtering**: Can exclude very low confidence results automatically
3. **⚖️ Balanced Information**: Combines authority with content quality and recency
4. **📋 Transparent Scoring**: Users understand why sources are rated differently
5. **🚀 Performance Optimization**: RAG weights help focus on most reliable content

This confidence scoring system ensures your neighborhood search results are **reliable, relevant, and up-to-date**! 🎯

---

## 🛠️ Troubleshooting

### Common Issues:

#### Low Scores for Good Sources:

- **Cause**: Domain not in authority database
- **Solution**: Add domain to `authority_scores` dict

#### High Scores for Poor Content:

- **Cause**: Technical quality overriding content issues
- **Solution**: Review quality indicators and patterns

#### Inconsistent Recency Scoring:

- **Cause**: Date format not recognized
- **Solution**: Add date patterns to `recent_indicators`

### Debug Mode:

Enable detailed logging in `confidence_scorer.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

---

_Last updated: 2025-06-27 | ZyoniaRAG v2.0_
