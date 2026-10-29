import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('../deliverables/CampusAI_Expanded_Final.pptx'));
await fs.mkdir('revision-export',{recursive:true});
for(let i=0;i<p.slides.items.length;i++) await fs.writeFile(`revision-export/slide-${i+1}.png`,new Uint8Array(await (await p.export({slide:p.slides.items[i],format:'png',scale:1})).arrayBuffer()));
console.log('Rendered final export:',p.slides.items.length);

