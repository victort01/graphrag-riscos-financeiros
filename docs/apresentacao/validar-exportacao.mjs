import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [runtimeRoot, skillDir, repo] = process.argv.slice(2);
if (!runtimeRoot || !skillDir || !repo) throw new Error('Informe raiz do runtime, diretório da skill e repositório.');
process.env.RUNTIME_NODE_MODULES = path.join(runtimeRoot,'node/node_modules');
const {finalizePresentation} = await import(pathToFileURL(path.join(skillDir,'container_tools/artifact_tool_utils.mjs')));
const base=path.join(repo,'docs/apresentacao');
const result=await finalizePresentation({
  workspaceDir:repo,
  candidatePath:path.join(base,'.build/candidate.pptx'),
  finalPath:path.join(base,'apresentacao-revisao.pptx'),
  pythonExecutable:path.join(runtimeRoot,'python/python.exe'),
  integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',
    ...[3,10,12].flatMap(n=>['--require-native-table-slide',String(n)])],
  explicitTotalSlideCount:14,
  requiredNativeTableOwnerSlides:[3,10,12],
  requiredNativeChartOwnerSlides:[],
  fontPolicy:{basis:'design',families:['Arial']},
  verifyArtifactToolImport:true,
  receiptPath:path.join(repo,'data/reports/validacao-apresentacao.json'),
});
console.log(JSON.stringify(result));
