// Общие SVG-ассеты серии (стиль: плоский 2D, тёмная тревожная палитра)
const P={bg:'#080b14',bg2:'#111827',bg3:'#1b2438',rock:'#3a2a2c',rockHi:'#7a3b32',glow:'#ff4a2e',
 win:'#f2c14e',skin:'#c9a58a',jacket:'#2f4a5a',jacketD:'#223644',pants:'#1d2430',hair:'#1a1412',ink:'#05070c',white:'#e9eef5'};
const ART={
artyom:(o={})=>`<g class="artyom" ${o.t?`transform="${o.t}"`:''}>
 <ellipse cx="0" cy="212" rx="55" ry="9" fill="#000" opacity=".4"/>
 <g class="legL"><rect x="-30" y="120" width="26" height="90" rx="9" fill="${P.pants}"/><rect x="-36" y="198" width="38" height="14" rx="6" fill="${P.ink}"/></g>
 <g class="legR"><rect x="4" y="120" width="26" height="90" rx="9" fill="${P.pants}"/><rect x="2" y="198" width="38" height="14" rx="6" fill="${P.ink}"/></g>
 <g class="armL"><rect x="-62" y="38" width="22" height="82" rx="10" fill="${P.jacketD}"/><circle cx="-51" cy="124" r="11" fill="${P.skin}"/></g>
 <rect x="-44" y="30" width="88" height="110" rx="22" fill="${P.jacket}"/>
 <rect x="-3" y="34" width="6" height="100" fill="${P.jacketD}"/>
 <g class="armR"><rect x="40" y="38" width="22" height="82" rx="10" fill="${P.jacketD}"/><circle cx="51" cy="124" r="11" fill="${P.skin}"/></g>
 <g class="head"><rect x="-10" y="14" width="20" height="22" fill="${P.skin}"/>
 <ellipse cx="0" cy="-8" rx="36" ry="40" fill="${P.skin}"/>
 <path d="M-38 -12 Q-34 -52 0 -50 Q36 -52 38 -12 Q20 -30 -6 -26 Q-26 -24 -38 -12Z" fill="${P.hair}"/>
 <g class="eyes"><circle cx="-13" cy="-4" r="${o.scared?7:5}" fill="${P.white}"/><circle cx="13" cy="-4" r="${o.scared?7:5}" fill="${P.white}"/>
 <circle cx="-12" cy="-3" r="2.6" fill="${P.ink}"/><circle cx="14" cy="-3" r="2.6" fill="${P.ink}"/></g>
 <path d="${o.scared?'M-10 20 Q0 12 10 20':'M-9 18 Q0 21 9 18'}" stroke="${P.ink}" stroke-width="3" fill="none" stroke-linecap="round"/>
 <path d="M-22 -16 L-6 -20 M6 -20 L22 -16" stroke="${P.hair}" stroke-width="4" stroke-linecap="round"/></g></g>`,
kim:(o={})=>`<g class="kim" ${o.t?`transform="${o.t}"`:''}>
 <rect x="-46" y="30" width="92" height="120" rx="24" fill="#4a4358"/>
 <rect x="-12" y="30" width="24" height="60" fill="${P.white}" opacity=".85"/>
 <ellipse cx="0" cy="-8" rx="36" ry="40" fill="#b9977e"/>
 <path d="M-40 -6 Q-40 -56 0 -54 Q40 -56 40 -6 Q30 -34 0 -32 Q-30 -34 -40 -6Z" fill="#cfd3da"/>
 <circle cx="-13" cy="-2" r="14" fill="none" stroke="${P.ink}" stroke-width="3"/><circle cx="13" cy="-2" r="14" fill="none" stroke="${P.ink}" stroke-width="3"/>
 <path d="M-1 -2 H1" stroke="${P.ink}" stroke-width="3"/>
 <circle cx="-13" cy="-2" r="3" fill="${P.ink}"/><circle cx="13" cy="-2" r="3" fill="${P.ink}"/>
 <path d="M-9 20 H9" stroke="${P.ink}" stroke-width="3" stroke-linecap="round"/></g>`,
asteroid:(o={})=>`<g class="asteroid" ${o.t?`transform="${o.t}"`:''}>
 <circle r="${o.r||200}" fill="${P.glow}" opacity=".10"/><circle r="${(o.r||200)*0.82}" fill="${P.glow}" opacity=".12"/>
 <path d="M-170 -40 Q-150 -150 -40 -170 Q70 -190 150 -110 Q200 -20 160 70 Q110 170 0 180 Q-120 190 -175 90 Q-195 20 -170 -40Z" fill="${P.rock}"/>
 <path d="M-170 -40 Q-150 -150 -40 -170 Q70 -190 150 -110 Q130 -90 90 -110 Q20 -140 -60 -100 Q-130 -60 -170 -40Z" fill="${P.rockHi}" opacity=".65"/>
 <path d="M-120 -10 l40 30 l-5 45 M20 -60 l-10 50 l40 30 M95 40 l40 20" stroke="${P.ink}" stroke-width="5" fill="none" stroke-linecap="round"/>
 <ellipse cx="-30" cy="20" rx="34" ry="22" fill="#241a1c" transform="rotate(-20 -30 20)"/><ellipse cx="110" cy="-30" rx="16" ry="10" fill="#241a1c"/><ellipse cx="-110" cy="100" rx="14" ry="9" fill="#241a1c"/>
 ${o.lights?`<g class="lights" fill="#fff">${[-90,-45,0,45,90].map(x=>`<circle cx="${x}" cy="120" r="9"/><circle cx="${x}" cy="120" r="22" opacity=".25"/>`).join('')}</g>`:''}</g>`,
building:(x,y,w,h,lit=[])=>{let s=`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${P.bg3}"/>`;
 for(let r=0;r<Math.floor(h/46);r++)for(let c=0;c<Math.floor(w/38);c++){const on=lit.includes(r*10+c);
 s+=`<rect x="${x+10+c*38}" y="${y+14+r*46}" width="22" height="28" fill="${on?P.win:'#0d1220'}"/>`}return s},
sky:(w,h)=>{let s=`<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05070f"/><stop offset=".7" stop-color="#1a1424"/><stop offset="1" stop-color="#3a1a1c"/></linearGradient></defs><rect width="${w}" height="${h}" fill="url(#sk)"/>`;
 for(let i=0;i<70;i++){const a=Math.sin(i*91.7)*43758.5,b=Math.sin(i*12.9)*24634.6;s+=`<circle cx="${(a-Math.floor(a))*w}" cy="${(b-Math.floor(b))*h*.7}" r="${1+((i*7)%3)*.6}" fill="#fff" opacity="${.3+((i*13)%6)/10}"/>`}return s}
};
if(typeof module!=='undefined')module.exports={ART,P};
