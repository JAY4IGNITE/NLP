import fs from 'node:fs/promises';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('C:/Users/ramuv/Downloads/CampusNLP_updated.pptx'));
const inspection=await p.inspect({select:'$.slides[*]',include:['id','index','layout','elements.id','elements.kind','elements.text','elements.position','elements.style']});
await fs.writeFile('source-inspect.json',JSON.stringify(inspection.records,null,2));
await fs.mkdir('source',{recursive:true});
for(let i=0;i<p.slides.items.length;i++){
 const s=p.slides.items[i];
 await fs.writeFile(`source/slide-${i+1}.png`,new Uint8Array(await (await p.export({slide:s,format:'png',scale:0.8})).arrayBuffer()));
}
console.log('Rendered',p.slides.items.length);
