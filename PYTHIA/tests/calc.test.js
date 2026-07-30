/* PYTHIA -- tests for the calculation engine.
 *
 * Run with:  node tests/calc.test.js
 *
 * No dependencies and no test framework: the engine touches no DOM, so a
 * bare global is enough to load it. Expected values are taken from
 * standard references and worked examples, not from a previous run of
 * this code, which would only prove it is consistent with itself.
 *
 * Exits non-zero on any failure, so it can gate a commit.
 */

"use strict";

const fs = require("fs");
const path = require("path");

global.window = global;
const root = path.join(__dirname, "..");
new Function(fs.readFileSync(path.join(root, "data/elements.js"), "utf8"))();
new Function(fs.readFileSync(path.join(root, "js/calc.js"), "utf8"))();
const C = global.PYTHIA.calc;

let pass=0, fail=0;
function near(label, got, want, tol){
  const ok = Math.abs(got-want) <= (tol===undefined?0.005:tol);
  ok?pass++:fail++;
  console.log((ok?'  ok  ':'  FAIL'), label.padEnd(44), got.toFixed(5), ok?'':('want '+want));
}
function eq(label, got, want){
  const ok = JSON.stringify(got)===JSON.stringify(want);
  ok?pass++:fail++;
  console.log((ok?'  ok  ':'  FAIL'), label.padEnd(44), JSON.stringify(got), ok?'':('want '+JSON.stringify(want)));
}
function throws(label, fn, code){
  let got=null; try{ fn(); }catch(e){ got=e.code; }
  const ok = got===code; ok?pass++:fail++;
  console.log((ok?'  ok  ':'  FAIL'), label.padEnd(44), got, ok?'':('want '+code));
}

console.log('MOLAR MASS');
near('H2O',            C.molarMass('H2O').total, 18.015);
near('C6H12O6',        C.molarMass('C6H12O6').total, 180.156, 0.01);
near('Ca(OH)2',        C.molarMass('Ca(OH)2').total, 74.093, 0.01);
near('Fe2(SO4)3',      C.molarMass('Fe2(SO4)3').total, 399.88, 0.02);
near('CuSO4.5H2O',     C.molarMass('CuSO4.5H2O').total, 249.685, 0.02);
near('NaCl',           C.molarMass('NaCl').total, 58.443, 0.01);
eq  ('Ca2+ charge',    C.parseFormula('Ca2+').charge, 2);
eq  ('SO4-2 charge',   C.parseFormula('SO4-2').charge, -2);
eq  ('CuSO4 counts',   C.parseFormula('CuSO4').counts, {Cu:1,S:1,O:4});

console.log('\nMONOISOTOPIC');
near('H2O exact',      C.monoisotopicMass('H2O'), 18.010565, 1e-5);
near('C6H12O6 exact',  C.monoisotopicMass('C6H12O6'), 180.063388, 1e-4);
near('C2H6O exact',    C.monoisotopicMass('C2H6O'), 46.041865, 1e-4);

console.log('\nISOTOPIC PATTERN  (M+1 should track carbon count x 1.1%)');
const g=C.isotopicPattern('C6H12O6');
near('glucose M peak',     g[0].mass, 180.0634, 1e-3);
near('glucose M+1 rel %',  g[1].relative, 6.7, 0.6);
const cl2=C.isotopicPattern('Cl2');
near('Cl2 M+2 rel % (~65)', cl2[1].relative, 64.9, 2);

console.log('\nBALANCING');
eq('CH4 + O2 -> CO2 + H2O',   C.balance('CH4 + O2 -> CO2 + H2O').coefficients, [1,2,1,2]);
eq('Fe + O2 -> Fe2O3',        C.balance('Fe + O2 -> Fe2O3').coefficients, [4,3,2]);
eq('C3H8 + O2 -> CO2 + H2O',  C.balance('C3H8 + O2 -> CO2 + H2O').coefficients, [1,5,3,4]);
eq('KMnO4+HCl->KCl+MnCl2+H2O+Cl2',
   C.balance('KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2').coefficients, [2,16,2,2,8,5]);
eq('Al + HCl -> AlCl3 + H2',  C.balance('Al + HCl -> AlCl3 + H2').coefficients, [2,6,2,3]);

console.log('\nACIDS AND BASES');
near('strong acid 0.01 M',    C.pH.strongAcid(0.01), 2);
near('strong base 0.01 M',    C.pH.strongBase(0.01), 12);
near('acetic 0.1 M pKa 4.76', C.pH.weakAcid(0.1, 4.76).pH, 2.88, 0.01);
near('  its % dissociated',   C.pH.weakAcid(0.1, 4.76).dissociated, 1.32, 0.05);
near('ammonia 0.1 M pKb 4.75',C.pH.weakBase(0.1, 4.75).pH, 11.13, 0.01);
near('buffer equal parts',    C.pH.buffer(4.76, 0.1, 0.1), 4.76);
near('buffer 10:1',           C.pH.buffer(4.76, 1.0, 0.1), 5.76);

console.log('\nSTOICHIOMETRY AND DILUTION');
const lim=C.limitingReagent([
  {name:'H2', mass:10, molarMass:2.016, coefficient:2},
  {name:'O2', mass:64, molarMass:31.998, coefficient:1}]);
eq('limiting of H2/O2',       lim.limiting.name, 'O2');
near('  extent (mol)',        lim.extent, 2.0, 0.01);
near('atom economy',          C.atomEconomy(180, 250), 72);
near('E factor',              C.eFactor(45, 15), 3);
const d=C.dilution({c1:1, v1:null, c2:0.1, v2:100});
near('dilution solves v1',    d.value, 10);
eq('  solved for',            d.solvedFor, 'v1');
eq('serial 1:10 x3 last',     C.serialDilution(1,10,3).pop().concentration, 0.001);

console.log('\nUNITS');
near('100 C -> F',            C.temperature.convert(100,'C','F'), 212);
near('0 C -> K',              C.temperature.convert(0,'C','K'), 273.15);
near('-40 C -> F',            C.temperature.convert(-40,'C','F'), -40);
near('1 atm -> mmHg',         C.convertPressure(1,'atm','mmHg'), 760, 0.01);
near('1 bar -> psi',          C.convertPressure(1,'bar','psi'), 14.5038, 0.001);

console.log('\nERRORS ARE REPORTED, NOT GUESSED');
throws('unknown element',     ()=>C.molarMass('Xx2O'), 'UNKNOWN_ELEMENT');
throws('unbalanced bracket',  ()=>C.molarMass('Ca(OH2'), 'UNBALANCED_BRACKET');
throws('empty formula',       ()=>C.molarMass(''), 'EMPTY_FORMULA');
throws('negative concentration',()=>C.pH.strongAcid(-1), 'MUST_BE_POSITIVE');
throws('below absolute zero', ()=>C.temperature.convert(-300,'C','K'), 'BELOW_ABSOLUTE_ZERO');
throws('equation with no arrow',()=>C.balance('CH4 + O2'), 'NEEDS_TWO_SIDES');
throws('two blanks in dilution',()=>C.dilution({c1:1,v1:null,c2:null,v2:100}), 'LEAVE_ONE_BLANK');

console.log('\n'+pass+' passed, '+fail+' failed');
process.exit(fail?1:0);
