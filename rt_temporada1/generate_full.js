const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, PageBreak, convertInchesToTwip,
} = require("docx");

const PAGE = { width: 12240, height: 15840 }; // US Letter
const MARGIN = convertInchesToTwip(1);

const TITLES = {
  1: "El Parque",
  2: "La Pared",
  3: "Nayeli",
  4: "La Frontera",
  5: "Consecuencias",
  6: "Grietas",
  7: "El Puente",
  8: "Ferro",
  9: "El Precio del Silencio",
  10: "La Bala",
  11: "Después del Disparo",
  12: "Caída",
  13: "El Golpe",
  14: "Volver",
  15: "Lo Que Queda",
  16: "La Traición",
  17: "El Plan",
  18: "La Vía del Tren",
  19: "Alex",
  20: "El Bosque",
};

function buildChapterParagraphs(rawText) {
  const lines = rawText.split("\n").map((l) => l.trim()).filter((l) => l.length > 0);
  const paragraphs = [];
  const dialogueRe = /^([A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ' ]*):\s*—(.*)$/;

  for (const line of lines) {
    if (line === "***") {
      paragraphs.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 200 },
        children: [new TextRun({ text: "* * *" })],
      }));
      continue;
    }
    const dmatch = line.match(dialogueRe);
    if (dmatch) {
      const [, name, rest] = dmatch;
      paragraphs.push(new Paragraph({
        spacing: { after: 160 },
        children: [
          new TextRun({ text: `${name}: `, bold: true }),
          new TextRun({ text: `—${rest}` }),
        ],
      }));
    } else if (line.startsWith("(") && line.endsWith(")")) {
      paragraphs.push(new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun({ text: line, italics: true })],
      }));
    } else {
      paragraphs.push(new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun({ text: line })],
      }));
    }
  }
  return paragraphs;
}

const children = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 2400, after: 200 },
    children: [new TextRun({ text: "R.T.", bold: true, size: 96 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 4800 },
    children: [new TextRun({ text: "Temporada 1", size: 32, italics: true })],
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

for (let n = 1; n <= 20; n++) {
  const num = String(n).padStart(2, "0");
  const filePath = path.join(__dirname, `capitulo_${num}.txt`);
  const rawText = fs.readFileSync(filePath, "utf8");
  const paragraphs = buildChapterParagraphs(rawText);

  children.push(new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: n === 1 ? 0 : 0, after: 60 },
    children: [new TextRun({ text: `Capítulo ${n}` })],
  }));
  children.push(new Paragraph({
    spacing: { after: 400 },
    children: [new TextRun({ text: TITLES[n], italics: true, size: 26 })],
  }));
  children.push(...paragraphs);

  if (n < 20) {
    children.push(new Paragraph({ children: [new PageBreak()] }));
  }
}

const doc = new Document({
  sections: [
    {
      properties: {
        page: { size: PAGE, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } },
      },
      children,
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const outPath = path.join(__dirname, "RT_Temporada_1_Completa.docx");
  fs.writeFileSync(outPath, buffer);
  console.log("Escrito:", outPath);
});
