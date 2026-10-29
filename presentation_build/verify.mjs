import fs from 'node:fs/promises';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('../deliverables/CampusAI_Project_Presentation.pptx'));
await fs.mkdir('export-preview',{recursive:true});
for(let i=0;i<p.slides.items.length;i++)await fs.writeFile(`export-preview/slide-${i+1}.png`,new Uint8Array(await (await p.export({slide:p.slides.items[i],format:'png',scale:1})).arrayBuffer()));
console.log('Final exported deck rendered:',p.slides.items.length);
