import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';
const root='C:/Users/ramuv/NLP_project';
const source='C:/Users/ramuv/Downloads/CampusNLP_updated.pptx';
const skill='C:/Users/ramuv/.codex/plugins/cache/openai-primary-runtime/presentations/26.1022.11436/skills/presentations';
const p=await PresentationFile.importPptx(await FileBlob.load(source));
const snapshots=JSON.parse(await fs.readFile('source-inspect.json','utf8'));
const fonts=['Times New Roman','Calibri'];
function shape(id){return p.resolve(id);}
function replace(id,text){shape(id).text=text;}
function body(id,rows,{red=false,size=20,space=15}={}){
 const s=shape(id);
 s.text=rows.map(([label,copy])=>({bulletCharacter:'',marginLeft:0,indent:0,spaceAfter:space,runs:[{run:label+' ',style:{bold:true,color:red?'#FF0000':'#000000',typeface:'Times New Roman',fontSize:`${size}pt`}},{run:copy,style:{bold:false,color:'#000000',typeface:'Times New Roman',fontSize:`${size}pt`}}]}));
 s.text.style={typeface:'Times New Roman',fontSizePt:size,color:'#000000',alignment:'left',verticalAlignment:'top',autoFit:'none',insets:{left:8,right:8,top:5,bottom:5}};
}
function groups(id,rows){
 const s=shape(id);
 s.text=rows.flatMap(([label,copy])=>[
 {bulletCharacter:'',marginLeft:0,indent:0,spaceAfter:5,runs:[{run:label,style:{bold:true,color:'#FF0000',typeface:'Times New Roman',fontSize:'20pt'}}]},
 {bulletCharacter:'',marginLeft:0,indent:0,spaceAfter:18,runs:[{run:copy,style:{bold:false,color:'#000000',typeface:'Times New Roman',fontSize:'20pt'}}]}
 ]);
 s.text.style={typeface:'Times New Roman',fontSizePt:20,alignment:'left',verticalAlignment:'top',autoFit:'none',insets:{left:8,right:8,top:5,bottom:5}};
 for (const [label] of rows) s.text.get(label).fill='#FF0000';
}
replace('sh/qhsbq9k7','CampusAI: Intelligent Multi-Department\nAcademic Helpdesk');
shape('sh/qhsbq9k7').position={left:64,top:260,width:1152,height:130};
shape('sh/qhsbq9k7').text.style={typeface:'Calibri',fontSizePt:30,bold:true,color:'#21409A',alignment:'center',verticalAlignment:'middle'};
replace('sh/tofapkju','Team Members:\nV. Jaya Sai Krishna  (24B11CS514)\nY. Pavanputra  (24B11CS504)\nK. Krishna Vardhan  (24B11CS237)\nK. Mohan Vamsi Reddy  (24B11CS197)');
shape('sh/tofapkju').position={left:160,top:440,width:960,height:210};
shape('sh/tofapkju').text.style={typeface:'Calibri',fontSizePt:18,bold:true,color:'#0070C0',alignment:'center',verticalAlignment:'top'};
// Match the original agenda structure, with preprocessing and retrieval under Modules.
body('sh/fm90n29w',[
 ['Project overview:','CampusAI is an academic helpdesk for Aditya University. It interprets student questions and retrieves curriculum evidence with document and page references.'],
 ['Application domain:','Natural Language Processing and Information Retrieval for B.Tech Curriculum 2024, Version 3.0, across eight engineering departments.'],
 ['Student needs:','Students can ask about course codes, credits, semester subjects, syllabus units, prerequisites, and academic regulations.'],
 ['Project objective:','Combine intent classification, exact database lookup, and hybrid document retrieval to make academic answers easier to find and verify.']
]);
body('sh/ri58ba1c',[
 ['Existing problem:','Academic information spans eight curriculum PDFs containing 6,502 pages. Students must identify the correct department, semester, and source page.'],
 ['Search difficulties:','Abbreviations, paraphrases, and Telugu-English queries can obscure intent. Similar course names also require department context.'],
 ['Risk of incorrect answers:','Wrong credits, prerequisites, or semester details can mislead academic planning. A fluent answer alone does not establish accuracy.'],
 ['Affected users:','Students seeking academic guidance and staff who repeatedly answer curriculum questions.'],
 ['Required improvement:','Route factual questions to structured records and support descriptive answers with traceable evidence, clarification, or abstention.']
],{space:14});
body('sh/zahkn2dg',[
 ['Query understanding:','Identify language, normalize academic terms, predict one of 30 intents, and extract course, department, semester, and unit entities.'],
 ['Exact academic facts:','Use SQL retrieval for structured details such as course codes, credits, and semester offerings.'],
 ['Syllabus and topic search:','Combine BM25 keyword retrieval with dense semantic search, fuse rankings with RRF, and rerank candidate passages.'],
 ['Evidence-based responses:','Generate answers from retrieved content, attach document and page references, and request clarification when the query is ambiguous.'],
 ['Student application:','A React and TypeScript interface connects to FastAPI for chat, course exploration, semester views, comparisons, and source viewing.']
],{space:14});
replace('sh/zipk7i5w','Proposed Workflow (System Architecture)');
replace('sh/nipobu1o','Query Understanding');
replace('sh/ojy54z29','Detect language, normalize academic terms, extract entities, and resolve context from earlier questions.');
replace('sh/a5g769kf','Intent Classification');
replace('sh/b6pofe10','Word and character TF-IDF features feed a soft-voting ensemble that predicts one of 30 academic and conversational intents.');
replace('sh/x8r6hojq','SQL and Hybrid Retrieval');
body('sh/y907a90b',[
 ['Structured facts:','Query academic database records.'],
 ['Document evidence:','Search BM25 and dense indices, combine results with Reciprocal Rank Fusion, and retain source metadata.']
],{size:16,space:5});
replace('sh/t4bq983y','Evidence Ranking and Checks');
replace('sh/83290nmd','Cross-encoder reranking prioritizes relevant passages. Citation checks and confidence rules support evidence selection.');
replace('sh/61kryd4n','Answer and Source Display');
replace('sh/h8vads3a','Return an answer with document and page references, ask for clarification, or report that sufficient evidence is unavailable.');
body('sh/q903y5on',[
 ['Official source corpus:','Eight Aditya University B.Tech Curriculum 2024 PDFs, Version 3.0, covering 6,502 pages.'],
 ['Department coverage:','CSE, CSE-DS, IT, ECE, EEE, Civil Engineering, Mining Engineering, and Petroleum Technology.'],
 ['Structured academic catalog:','569 registered courses, 583 syllabus units, and 1,273 textbook references.'],
 ['Intent dataset:','1,201 labeled queries across 30 classes. Fields include query, intent, domain, language, course, department, semester, and unit.'],
 ['Training and evaluation:','A stratified 80/20 split gives 960 training and 241 test queries. Separate stratified five-fold cross-validation estimates model stability.'],
 ['Data formats:','PDF source documents, a CSV query dataset, JSON metadata and indices, and a relational academic database.']
],{space:12});
groups('sh/sz2xszad',[
 ['Text Preprocessing and Query Understanding','Normalize case, punctuation, and whitespace while preserving course codes, academic acronyms, and Telugu text. Extract entities and handle follow-up or multi-intent questions.'],
 ['Intent Classification','Combine word and character TF-IDF features with calibrated Linear SVM, Logistic Regression, and Complement Naive Bayes. Confidence and alternative intents support query routing.'],
 ['Retrieval, Grounding, and Application','Retrieve exact facts through SQL and descriptive evidence through hybrid search. The RAG layer adds citations, while the web app provides chat, course exploration, comparisons, and PDF source viewing.']
]);
groups('sh/cjqpormh',[
 ['Intent Classification: TF-IDF and Soft Voting','Word n-grams (1–3) and character n-grams (2–5) capture phrases and spelling patterns. Calibrated Linear SVM, Logistic Regression, and Complement Naive Bayes combine probabilities with weights of 2:2:1.'],
 ['Semantic Retrieval: BM25, MiniLM, and RRF','BM25 matches academic keywords. all-MiniLM-L6-v2 produces 384-dimensional embeddings for semantic matching. Reciprocal Rank Fusion combines both rankings, followed by MiniLM cross-encoder reranking.'],
 ['Grounding and Response Control','SQL provides structured academic facts. Retrieved passages supply answer evidence and page references. Confidence checks, clarification, and abstention reduce unsupported answers but do not guarantee correctness.']
]);
groups('sh/hsn6t4bq',[
 ['Student-Facing Output','The web app supports academic chat, course exploration, semester browsing, and cross-department comparison. Answers include source references with access to the relevant PDF page.'],
 ['Intent Classifier Results','The latest report records 96.27% top-1 accuracy and 99.17% top-3 accuracy on 241 test queries across 30 classes. Macro F1 is 0.9196 and weighted F1 is 0.9614.'],
 ['Cross-Validation and Interpretation','Five-fold accuracy averages 96.00% with a standard deviation of 1.17 percentage points. These are classifier results on the project dataset, not a measure of end-to-end answer correctness.']
]);
groups('sh/e1wja5wz',[
 ['Conclusion','CampusAI integrates NLP query understanding, structured academic lookup, and hybrid evidence retrieval for eight departments. The latest intent classifier reaches 96.27% accuracy on the held-out project test set.'],
 ['Current Limitations','Coverage centres on Curriculum 2024, Version 3.0. The test set is small for some intents, and out-of-scope detection has an F1 score of 0.40. Retrieval relevance and answer correctness need independent evaluation.'],
 ['Future Scope','Collect student queries across languages, strengthen low-performing intents, and evaluate retrieval against human relevance labels. Expand verified curriculum coverage and connect approved live academic notices.']
]);
// Keep the template title hierarchy, while removing trailing blank paragraphs.
replace('sh/0ni1w7q1','Introduction');
replace('sh/14n2lkvq','Conclusion and Future Scope');
const notes=[
 'CampusAI project presentation. Project name and scope: backend/config.py and README.md. Team names and IDs retained from the supplied CampusNLP_updated.pptx.',
 'The presentation follows the supplied template section order. Modules covers text preprocessing, intent classification, and semantic retrieval and grounding.',
 'Sources: backend/config.py, backend/rag/generator.py, data/structured/resource_catalog.json. Scope: B.Tech Curriculum 2024 Version 3.0.',
 'Sources: data/manifests/source_quality_report.json, backend/nlp/entity_extractor.py, backend/nlp/coreference.py. Corpus counts are manifest values.',
 'Sources: backend/nlp/intent_classifier.py, scripts/train_intent_model.py, backend/rag/retriever.py, backend/rag/generator.py, frontend/src. Capabilities describe implemented components, not guarantees of answer correctness.',
 'Sources: backend/nlp/preprocessing.py, backend/nlp/normalizer.py, backend/nlp/entity_extractor.py, backend/rag/retriever.py, backend/rag/reranker.py, backend/rag/generator.py, backend/rag/citation_verifier.py. Reranking and LLM behavior depend on runtime configuration.',
 'Sources: data/manifests/source_quality_report.json (8 PDFs, 6,502 pages), data/structured/resource_catalog.json (catalog counts), data/aditya_university_queries.csv (1,201 rows, 30 intents), scripts/train_intent_model.py (stratified 20% test split, random seed 42), reports/classification_report.txt (241 test samples). The remaining 960 queries form the training split. Cross-validation runs separately over the full dataset. Counts replace the older synthetic CampusFAQ-50K figures in the template.',
 'Sources: backend/nlp/preprocessing.py, scripts/train_intent_model.py, backend/nlp/intent_classifier.py, backend/rag/retriever.py, backend/rag/generator.py, frontend/src. Stopword removal defaults to disabled. Lemmatization is conditional on available NLTK resources.',
 'Sources: scripts/train_intent_model.py (feature ranges, ensemble members and 2:2:1 voting weights), data/structured/resource_catalog.json (384-dimensional MiniLM and retrieval components), backend/rag/retriever.py, backend/rag/citation_verifier.py. The cited ensemble is the latest trained model architecture.',
 'Sources: reports/model_metrics.json, timestamp 2026-10-22 08:09:45 UTC, and reports/classification_report.txt. Dataset: 1,201 queries, 30 intents. Test: 241 queries. Top-1 0.9627, top-3 0.9917, macro F1 0.9196, weighted F1 0.9614, 5-fold CV mean 0.9600 and standard deviation 0.0117. These are saved evaluation results, not a new run. The retrieval metrics in backend/evaluation/benchmark_runner.py are hard-coded constants, so they are excluded as measured outcomes. The older 16-query benchmark uses substring checks for facts and is insufficient to establish general answer accuracy.',
 'Sources: reports/classification_report.txt (out_of_scope F1 0.4000 with support 3; admission_information F1 0.5714 with support 4), docs/LIMITATIONS.md, backend/evaluation/benchmark_runner.py. Future work is proposed work. The project dataset may not represent real student query distributions, and the current split is not an independently collected student evaluation.'
];
for(let i=0;i<p.slides.items.length;i++)p.slides.items[i].speakerNotes.text=notes[i];
await fs.mkdir('draft',{recursive:true});
await fs.mkdir('final-preview',{recursive:true});
await (await PresentationFile.exportPptx(p)).save('draft/CampusAI.pptx');
for(let i=0;i<p.slides.items.length;i++){
 await fs.writeFile(`final-preview/slide-${i+1}.png`,new Uint8Array(await (await p.export({slide:p.slides.items[i],format:'png',scale:1})).arrayBuffer()));
}
await fs.writeFile('final-inspect.json',JSON.stringify((await p.inspect({select:'$.slides[*]',include:['id','index','elements.text','elements.position','elements.style','notes.text']})).records,null,2));
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({
 workspaceDir:root,candidatePath:path.join(root,'presentation_build/draft/CampusAI.pptx'),finalPath:path.join(root,'deliverables/CampusAI_Project_Presentation.pptx'),
 pythonExecutable:'C:/Users/ramuv/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12193588,6858000','--validate-bullet-geometry','--validate-heading-fit'],explicitTotalSlideCount:11,
 fontPolicy:{basis:'reference',families:fonts,referencePath:source,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex')},
 verifyArtifactToolImport:true,receiptPath:path.join(root,'presentation_build/validation.json')
});
console.log(JSON.stringify(result));
