# Data Source Documentation

**Date**: 2025-10-02
**Feature**: PDF Monograph to Structured JSON Conversion

---

## Source Website

**URL**: https://monografiasfloradobrasil.jbrj.gov.br/

**Title**: Lista de Monografias - Flora do Brasil 2020

**Institution**: Jardim Botânico do Rio de Janeiro (JBRJ)

---

## Monograph Organization

The PDF monographs are organized by **taxonomic family** (família).

### Directory Structure

```
monografias/
├── Acanthaceae/
├── Achatocarpaceae/
├── Adoxaceae/
├── Aizoaceae/
├── Alismataceae/
├── ... (103 more families)
└── Zygophyllaceae/
```

---

## Available Families

The website provides monographs for **107 botanical families** across two major groups:

### 1. Algas (Algae)
- Taxonomic group with algae families

### 2. Angiospermas (Angiosperms)
- The majority of monographs belong to this group
- Includes 107 families listed below

---

## Complete Family List (Angiosperms)

1. Acanthaceae
2. Achatocarpaceae
3. Adoxaceae
4. Aizoaceae
5. Alismataceae
6. Amaranthaceae
7. Amaryllidaceae
8. Anacardiaceae
9. Annonaceae
10. Apiaceae
11. Apocynaceae
12. Aquifoliaceae
13. Araceae
14. Araliaceae
15. Arecaceae
16. Aristolochiaceae
17. Asparagaceae
18. Asteraceae
19. Balanophoraceae
20. Basellaceae
21. Begoniaceae
22. Berberidaceae
23. Bignoniaceae
24. Bixaceae
25. Boraginaceae
26. Brassicaceae
27. Bromeliaceae
28. Burmanniaceae
29. Burseraceae
30. Cactaceae
31. Calceolariaceae
32. Campanulaceae
33. Cannabaceae
34. Cannaceae
35. Capparaceae
36. Cardiopteridaceae
37. Caricaceae
38. Caryocaraceae
39. Caryophyllaceae
40. Celastraceae
41. Chloranthaceae
42. Chrysobalanaceae
43. Cistaceae
44. Cleomaceae
45. Clusiaceae
46. Columelliaceae
47. Combretaceae
48. Commelinaceae
49. Connaraceae
50. Convolvulaceae
51. Costaceae
52. Crassulaceae
53. Cucurbitaceae
54. Cunoniaceae
55. Cymodoceaceae
56. Cyperaceae
57. Dichapetalaceae
58. Dilleniaceae
59. Dioscoreaceae
60. Droseraceae
61. Ebenaceae
62. Elaeocarpaceae
63. Ericaceae
64. Eriocaulaceae
65. Erythroxylaceae
66. Euphorbiaceae
67. Fabaceae
68. Gentianaceae
69. Geraniaceae
70. Gesneriaceae
71. Goodeniaceae
72. Haemodoraceae
73. Haloragaceae
74. Heliconiaceae
75. Humiriaceae
76. Hydrocharitaceae
77. Hydroleaceae
78. Hypericaceae
79. Hypoxidaceae
80. Icacinaceae
81. Iridaceae
82. Iteaceae
83. Ixonanthaceae
84. Krameriaceae
85. Lamiaceae
86. Lauraceae
87. Lecythidaceae
88. Lentibulariaceae
89. Linaceae
90. Loganiaceae
91. Loranthaceae
92. Lythraceae
93. Malpighiaceae
94. Malvaceae
95. Marantaceae
96. Marcgraviaceae
97. Martyniaceae
98. Mayacaceae
99. Melastomataceae
100. Meliaceae
101. Menispermaceae
102. Monimiaceae
103. Moraceae
104. Muntingiaceae
105. Myoporaceae
106. Myristicaceae
107. Myrsinaceae
108. Myrtaceae
109. Nyctaginaceae
110. Nymphaeaceae
111. Ochnaceae
112. Olacaceae
113. Oleaceae
114. Onagraceae
115. Opiliaceae
116. Orchidaceae
117. Orobanchaceae
118. Oxalidaceae
119. Passifloraceae
120. Pentaphylacaceae
121. Peraceae
122. Petiveriaceae
123. Phyllanthaceae
124. Phytolaccaceae
125. Picramniaceae
126. Piperaceae
127. Pittosporaceae
128. Plantaginaceae
129. Plumbaginaceae
130. Poaceae
131. Podostemaceae
132. Polygalaceae
133. Polygonaceae
134. Pontederiaceae
135. Portulacaceae
136. Primulaceae
137. Proteaceae
138. Putranjivaceae
139. Quillajaceae
140. Ranunculaceae
141. Rapateaceae
142. Resedaceae
143. Rhamnaceae
144. Rosaceae
145. Rubiaceae
146. Rutaceae
147. Salicaceae
148. Santalaceae
149. Sapindaceae
150. Sapotaceae
151. Sarraceniaceae
152. Saururaceae
153. Schlegeliaceae
154. Schoepfiaceae
155. Scrophulariaceae
156. Simaroubaceae
157. Siparunaceae
158. Smilacaceae
159. Solanaceae
160. Sphenocleaceae
161. Staphyleaceae
162. Styracaceae
163. Symplocaceae
164. Talinaceae
165. Tamaricaceae
166. Tetrachondraceae
167. Theaceae
168. Thurniaceae
169. Thymelaeaceae
170. Tofieldiaceae
171. Trigoniaceae
172. Tropaeolaceae
173. Turneraceae
174. Typhaceae
175. Urticaceae
176. Verbenaceae
177. Violaceae
178. Vitaceae
179. Vivianiaceae
180. Vochysiaceae
181. Winteraceae
182. Ximeniaceae
183. Xyridaceae
184. Zingiberaceae
185. Zygophyllaceae

---

## Impact on System Design

### Processing Workflow

**Batch Processing Model**:
1. PDFs are placed in a single flat directory (`monografias/`)
2. System processes all PDFs in the directory
3. After successful processing, PDFs are deleted from the directory
4. New batch of PDFs is added to the directory
5. Process repeats

### Expected Directory Layout
```
monografias/
├── monografia_fabaceae_001.pdf
├── monografia_asteraceae_042.pdf
├── monografia_myrtaceae_015.pdf
└── ... (other PDFs in the same directory)
```

**No subdirectories** - all PDFs in a single flat structure.

### Directory Scanning Requirements
- Scan single directory (non-recursive)
- Process all `*.pdf` files found
- No need to extract family from directory structure
- Family information extracted from PDF content itself

### Post-Processing
- After successful extraction and MongoDB storage, PDFs can be removed
- System should support reprocessing if needed (idempotent based on PDF hash)
- Avoid reprocessing same PDF twice (check `source_pdf_hash` in MongoDB)

---

## References

- **Website**: https://monografiasfloradobrasil.jbrj.gov.br/
- **Institution**: Jardim Botânico do Rio de Janeiro
- **Project**: Flora do Brasil 2020
- **Last Verified**: 2025-10-02
