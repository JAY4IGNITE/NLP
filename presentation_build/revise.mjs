import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';

const root='C:/Users/ramuv/NLP_project';
const source='C:/Users/ramuv/Downloads/CampusNLP_updated.pptx';
const skill='C:/Users/ramuv/.codex/plugins/cache/openai-primary-runtime/presentations/26.1022.11436/skills/presentations';
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/deliverables/CampusAI_Project_Presentation.pptx'));
const originals=[...p.slides.items];
const added=[];
const red='#FF0000',blue='#21409A';
const docs='https://scikit-learn.org/stable/modules/generated/';

function text(slide,copy,x,y,w,h,{size=26.667,bold=false,color='#000000',align='left'}={}){
 const s=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 s.text=copy;
 s.text.style={typeface:'Times New Roman',fontSize:size,bold,color,alignment:align,verticalAlignment:'top',autoFit:'none',insets:0};
 return s;
}
async function page(title,notes){
 const s=originals[8].duplicate();added.push(s);
 const record=(await p.inspect({select:`$.slides[${p.slides.items.findIndex(x=>x.id===s.id)}]`,include:['id','elements.id','elements.text']})).records[0];
 for(const e of record.elements){if(e.text) p.delete(e.id);}
 text(s,title,230,36,990,84,{size:54,color:red,align:'center'});
 s.speakerNotes.text=notes;
 return s;
}
function sections(s,rows,{top=155,step=150}={}){
 rows.forEach(([heading,copy],i)=>{
  text(s,heading,74,top+i*step,1132,38,{color:red,bold:true});
  text(s,copy,74,top+43+i*step,1132,step-45);
 });
}
function foot(s,t){text(s,t,74,646,1132,40,{size:20,color:'#555555'});}
function table(s,values,widths,{top=170,height=400,size=25}={}){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:74,top,width:1132,height,columnWidths:widths,values});
 t.borders.assign({fill:'#B8C2D4',width:0.7,style:'solid'});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?blue:(r%2?'#FFFFFF':'#F1F4F9');
  cell.text.style={typeface:'Times New Roman',fontSize:size,color:r===0?'#FFFFFF':'#000000',bold:r===0,alignment:'left',verticalAlignment:'middle'};
 }
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({margins:{left:12,right:12,top:8,bottom:8}});
 return t;
}
async function screenshot(s,file,position,crop){
 s.images.add({blob:new Uint8Array(await fs.readFile(root+'/frontend/qa/screenshots/'+file)),contentType:'image/png',alt:'Recorded CampusAI application demonstration',position,fit:'contain',...(crop?{crop}: {})});
}

let s=await page('NLP Query Understanding','Sources: backend/nlp/preprocessing.py, backend/nlp/normalizer.py, backend/nlp/entity_extractor.py, backend/nlp/coreference.py, backend/nlp/multi_intent.py. Example illustrates parsing and does not assert a new model prediction.');
sections(s,[
 ['1. Language and text normalization','Recognize English, Telugu, or mixed queries. Normalize case, punctuation, and whitespace while preserving course codes and academic abbreviations. Lemmatization is optional when language resources are available.'],
 ['2. Academic entity extraction','Identify the course, department, semester, and unit independently of intent. For “Explain Unit 3 of Operating Systems in CSE,” the entities specify which syllabus content to retrieve.'],
 ['3. Context and ambiguity handling','Use earlier turns to interpret follow-up questions. Ask for clarification when an abbreviation has multiple meanings, and decompose requests that ask for more than one type of academic information.']
],{step:158});

s=await page('TF-IDF Feature Extraction','Sources: scripts/train_intent_model.py and '+docs+'sklearn.feature_extraction.text.TfidfVectorizer.html. The character analyzer is char_wb; sublinear_tf=True. This is feature extraction for intent classification, separate from dense retrieval embeddings.');
sections(s,[
 ['Word features: phrases of one to three words','Word n-grams preserve expressions such as “course credits” and “semester total credits.” TF-IDF reduces the influence of frequent terms and gives more weight to terms that distinguish queries.'],
 ['Character features: sequences of two to five characters','Character n-grams capture fragments within word boundaries. They provide additional signals for spelling variations and related word forms when exact full-word matches differ.'],
 ['FeatureUnion: one input for all classifiers','The pipeline concatenates word and character TF-IDF vectors. Sublinear term frequency reduces the effect of repeated terms. All three classifiers receive this same sparse feature representation.']
],{step:158});

s=await page('Linear SVM Classifier','Sources: scripts/train_intent_model.py; https://scikit-learn.org/stable/modules/calibration and '+docs+'sklearn.calibration.CalibratedClassifierCV.html. LinearSVC C=1.5, squared_hinge loss, L2 penalty; CalibratedClassifierCV cv=3. No individual SVM benchmark is reported.');
sections(s,[
 ['How it classifies a query','Linear SVM learns separating boundaries between intent classes in TF-IDF feature space. Its margin-based objective balances class separation against training errors.'],
 ['Why calibration is required','LinearSVC produces decision scores rather than native probabilities. Three-fold probability calibration converts these scores into estimates that can participate in soft voting.'],
 ['CampusAI configuration and role','The project uses C = 1.5, squared-hinge loss, and L2 regularization. The calibrated SVM receives two of the ensemble’s five weight units. Its standalone accuracy has not been separately reported.']
],{step:158});

s=await page('Logistic Regression and NB','Sources: scripts/train_intent_model.py; '+docs+'sklearn.linear_model.LogisticRegression.html; '+docs+'sklearn.naive_bayes.ComplementNB.html. LR uses C=5, lbfgs, max_iter=1000, class_weight=balanced. ComplementNB uses alpha=0.3 and norm=True. No standalone comparative scores are available.');
text(s,'Logistic Regression',74,155,540,42,{color:red,bold:true});
text(s,'Learns a weighted relationship between TF-IDF features and each intent. It produces class probabilities directly for the ensemble.',74,213,535,130);
text(s,'Balanced class weights give rarer classes more influence during training. The project uses C = 5.0, the lbfgs solver, and up to 1,000 iterations.',74,368,535,145);
text(s,'Voting weight: 2',74,554,535,40,{color:blue,bold:true});
text(s,'Complement Naive Bayes',668,155,538,42,{color:red,bold:true});
text(s,'Uses feature statistics from the other classes to score an intent. It offers a different statistical approach to sparse text classification.',668,213,538,130);
text(s,'Smoothing reduces the effect of unseen features. CampusAI sets alpha = 0.3 and enables weight normalization with norm = True.',668,368,538,145);
text(s,'Voting weight: 1',668,554,538,40,{color:blue,bold:true});

s=await page('Soft-Voting Ensemble','Sources: scripts/train_intent_model.py; '+docs+'sklearn.ensemble.VotingClassifier.html. The arithmetic illustration is hypothetical and not an observed model output. Confidence is not a probability of end-to-end answer correctness.');
sections(s,[
 ['Weighted probability combination','For each intent, the ensemble combines calibrated SVM, Logistic Regression, and Complement Naive Bayes probabilities. The final intent has the highest combined score.'],
 ['Voting rule','Combined score = (2 × SVM probability + 2 × LR probability + NB probability) / 5. The weights are project settings, not the result of a reported model-comparison study.'],
 ['Illustrative calculation','If the three probabilities for course_credits are 0.80, 0.70, and 0.60, its combined score is 0.72. This explains the voting rule; it is not a measured prediction.']
],{step:158});

s=await page('The 30 Intent Classes','Source: reports/model_metrics.json classes array. The six families below are explanatory groupings for the presentation, not a new learned hierarchy. All 30 class labels are represented in readable form.');
table(s,[
 ['Intent family','Count','Classes covered'],
 ['Course information','8','Code, credits, category, L-T-P-C, outcomes, prerequisites, full syllabus, textbooks'],
 ['Academic planning','8','Course comparison, degree credits, electives, honours/minors, minor streams, minor courses, semester subjects, semester credits'],
 ['Rules and regulations','5','Attendance, grading, internships, promotion, curriculum version'],
 ['University information','4','Academic calendar, admissions, exam timetable, institutional leadership'],
 ['Syllabus detail','2','Unit syllabus, laboratory experiments'],
 ['Conversation and scope','3','Greeting, thanks, out-of-scope queries']
],[270,110,752],{top:150,height:458,size:23});
foot(s,'Families group the existing labels for explanation. The classifier predicts one of the 30 individual intents.');

s=await page('Hybrid Retrieval Algorithms','Sources: backend/rag/retriever.py, backend/rag/embeddings.py, data/structured/resource_catalog.json. reciprocal_rank_fusion uses k=60 and rank positions starting at 1. The embedding model and fallback behavior depend on runtime availability.');
sections(s,[
 ['BM25: match specific academic terms','Sparse retrieval scores keyword relevance using term frequency, inverse document frequency, and document length. Exact course names and codes provide useful lexical signals.'],
 ['MiniLM: match semantic meaning','all-MiniLM-L6-v2 maps queries and document chunks to 384-dimensional vectors. Cosine similarity ranks passages by vector similarity, helping match related wording.'],
 ['Reciprocal Rank Fusion: combine both lists','RRF adds each passage’s contribution from its rank in each result list: weight / (60 + rank). A passage appearing near the top of both lists receives a stronger combined score.']
],{step:158});

s=await page('Reranking and Grounding','Sources: backend/rag/reranker.py, backend/rag/citation_verifier.py, backend/rag/prompt_builder.py, backend/rag/generator.py, backend/database/sql_retriever.py. CitationVerifier checks document IDs, positive page numbers, and mentioned course codes; it does not prove every claim is entailed by a source. Reranker uses lexical fallback if model loading or inference fails.');
sections(s,[
 ['Cross-encoder reranking','The reranker scores each query and candidate passage together, then selects the highest-ranked evidence. CampusAI uses a MiniLM cross-encoder with a lexical fallback if the model is unavailable.'],
 ['Exact lookup and answer generation','Structured questions use SQL academic records. Descriptive questions use retrieved passages as context for the answer generator. This separates factual lookup from free-text synthesis.'],
 ['Citation checks and response boundaries','Checks validate source identifiers, page numbers, and mentioned course codes. Missing evidence can trigger abstention or clarification. These checks improve traceability but do not prove every answer claim is correct.']
],{step:158});

s=await page('Output: Academic Chat','Source screenshot: frontend/qa/screenshots/chat-answer-desktop.png, captured by frontend/qa/verify.mjs from an earlier application UI. This is recorded application output, not a fresh execution. The returned fields and citation demonstrate behavior, not independent factual verification. Screenshot retains the original content.');
await screenshot(s,'chat-answer-desktop.png',{left:65,top:154,width:798,height:470},{left:0.32,top:0.16,right:0.15,bottom:0.39});
text(s,'Question',944,163,270,38,{color:red,bold:true});
text(s,'The student asks for Operating Systems credits in CSE.',944,207,270,110);
text(s,'Returned output',944,338,270,38,{color:red,bold:true});
text(s,'Course details, a document ID, and a page reference accompany the answer.',944,382,270,155);
foot(s,'Recorded application demo. The source reference supports inspection of the returned academic details.');

s=await page('Output: Source Inspection','Source screenshot: frontend/qa/screenshots/source-desktop.png. Recorded earlier application UI. The original PDF shown is page 29 of the CSE Data Science curriculum document. The screenshot documents a PDF viewer interaction, not a fresh validation of all returned facts.');
text(s,'Original curriculum page: Semester III',74,155,720,40,{color:blue,bold:true});
await screenshot(s,'source-desktop.png',{left:74,top:215,width:720,height:380},{left:0.315,top:0.235,right:0.315,bottom:0.484});
text(s,'Visible source context',840,167,365,38,{color:red,bold:true});
text(s,'The linked document opens at page 29. This enlarged excerpt shows its Semester III course table.',840,217,365,120);
text(s,'Verification workflow',840,365,365,38,{color:red,bold:true});
text(s,'A student can inspect the curriculum table and compare the cited course record with the answer.',840,416,365,148);
foot(s,'Recorded application demo. Page references make source checking possible; users should verify disputed details.');

s=await page('Results: Overall Performance','Sources: reports/model_metrics.json, saved 2026-10-22 08:09:45 UTC; reports/classification_report.txt; scripts/train_intent_model.py. 1,201 samples, 960 train, 241 test, stratified split, seed 42. 232/241 = 96.26556%, 239/241 = 99.17012%, inferred integer counts agree with rounded reported scores. CV runs independently over the full dataset. Retrieval constants from backend/evaluation/benchmark_runner.py are excluded.');
text(s,'1,201 labeled queries    30 intents    960 train / 241 test',74,144,1132,44,{size:28,bold:true,color:blue});
table(s,[
 ['Metric','Recorded result','Meaning'],
 ['Top-1 accuracy','96.27%','232 of 241 test queries classified correctly'],
 ['Top-3 accuracy','99.17%','Correct intent among the top three for 239 queries'],
 ['Macro F1','0.9196','Each intent receives equal weight'],
 ['Weighted F1','0.9614','Each intent contributes according to test support'],
 ['Five-fold CV accuracy','96.00% ± 1.17 pp','Mean accuracy and standard deviation across folds']
],[315,235,582],{top:209,height:356,size:25});
foot(s,'Saved evaluation from 22 October 2026. Scores describe intent classification on the project dataset.');

s=await page('Results: Performance by Intent','Source: reports/classification_report.txt, saved 2026-10-22. Selected categories show high-support strengths and lower-performing small classes. These are not all 30 intents. Support is held-out test sample count. No model-to-model improvement claim is made.');
table(s,[
 ['Selected intent','Test queries','F1 score','Interpretation'],
 ['Unit syllabus','46','1.0000','Largest test class'],
 ['Semester subjects','39','1.0000','Strong on this test set'],
 ['Full syllabus','15','0.9677','High precision and recall'],
 ['Course credits','13','0.9600','Some missed credit queries'],
 ['Admission information','4','0.5714','Needs more varied examples'],
 ['Institutional leadership','2','0.6667','Very small test support'],
 ['Out-of-scope','3','0.4000','Priority for improvement']
],[340,145,145,502],{top:154,height:424,size:24});
foot(s,'Small class sizes limit confidence. A separate student-query test set is needed to assess real-world performance.');

// Keep the existing introduction and conclusion; replace the two compressed sections.
const allRecords=(await p.inspect({select:'$.slides[*]',include:['id']})).records;
const ids=new Map(p.slides.items.map((x,i)=>[x.id,allRecords[i].id]));
const order=[...originals.slice(0,8),...added,originals[10]].map(x=>ids.get(x.id));
p.slides.keep(order);
p.slides.reorder(order);
const agenda=(await p.inspect({select:'$.slides[1].elements[*]',include:['id','text']})).records.find(x=>x.text?.startsWith('Introduction'));
const ag=p.resolve(agenda.id);
ag.text=['Introduction','Problem Definition','Proposed Solution','Proposed Workflow','Data Used','Modules','Core NLP and ML Algorithms','Application Output','Evaluation Results','Conclusion and Future Scope'].map((t,i)=>({bulletCharacter:'',marginLeft:0,indent:0,spaceAfter:14,runs:[{run:`${i+1}. ${t}`}]}));
ag.text.style={typeface:'Times New Roman',fontSizePt:20,color:red};

await fs.mkdir('revision-preview',{recursive:true});
await (await PresentationFile.exportPptx(p)).save('draft/CampusAI_Detailed.pptx');
for(let i=8;i<p.slides.items.length;i++)await fs.writeFile(`revision-preview/slide-${i+1}.png`,new Uint8Array(await (await p.export({slide:p.slides.items[i],format:'png',scale:1})).arrayBuffer()));
await fs.writeFile('revision-inspect.json',JSON.stringify((await p.inspect({select:'$.slides[*]',include:['id','index','title','elements.text','elements.position']})).records,null,2));
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:root,candidatePath:root+'/presentation_build/draft/CampusAI_Detailed.pptx',finalPath:root+'/deliverables/CampusAI_Expanded_Final.pptx',
 pythonExecutable:'C:/Users/ramuv/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12193588,6858000','--validate-bullet-geometry','--validate-heading-fit',...[14,19,20].flatMap(x=>['--require-native-table-slide',String(x)])],
 requiredNativeTableOwnerSlides:[14,19,20],explicitTotalSlideCount:21,
 fontPolicy:{basis:'reference',families:['Times New Roman','Calibri'],referencePath:source,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex')},
 verifyArtifactToolImport:true,receiptPath:root+'/presentation_build/expanded-final-validation.json'});
console.log(JSON.stringify({path:result.finalPath,slides:p.slides.items.length}));
