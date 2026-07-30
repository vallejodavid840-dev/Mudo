const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, PageBreak, convertInchesToTwip,
} = require("docx");

const PAGE = { width: 12240, height: 15840 }; // US Letter
const MARGIN = convertInchesToTwip(1);

function buildChapterParagraphs(rawText) {
  const lines = rawText.split("\n").map((l) => l.trim()).filter((l) => l.length > 0);
  const paragraphs = [];
  const dialogueRe = /^([A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ' ]*):\s*—(.*)$/;

  for (const line of lines) {
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

const chapterRaw = fs.readFileSync(path.join(__dirname, "capitulo_01.txt"), "utf8");
const chapterParagraphs = buildChapterParagraphs(chapterRaw);

const doc = new Document({
  sections: [
    {
      properties: {
        page: { size: PAGE, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } },
      },
      children: [
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
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          spacing: { after: 60 },
          children: [new TextRun({ text: "Capítulo 1" })],
        }),
        new Paragraph({
          spacing: { after: 400 },
          children: [new TextRun({ text: "El Parque", italics: true, size: 26 })],
        }),
        ...chapterParagraphs,
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const outPath = path.join(__dirname, "Capitulo_01.docx");
  fs.writeFileSync(outPath, buffer);
  console.log("Escrito:", outPath);
});
