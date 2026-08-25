import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const [speechPath, emotionPath, movePath, outputPath] = process.argv.slice(2);

if (!speechPath || !emotionPath || !movePath || !outputPath) {
  throw new Error(
    "Usage: build_reference_data.mjs <speech.xlsx> <emotion.xlsx> <move.xlsx> <output.json>",
  );
}

function rowsFromSheet(workbook, sheetName) {
  const sheet = workbook.worksheets.getItem(sheetName);
  const values = sheet.getUsedRange(true)?.values ?? [];
  if (values.length === 0) return [];
  const headers = values[0].map((value) => String(value ?? "").trim());
  return values
    .slice(1)
    .filter((row) => row.some((value) => value != null && String(value).trim() !== ""))
    .map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index] ?? null])));
}

function textValue(value) {
  return String(value ?? "").normalize("NFKC").replace(/\s+/g, " ").trim();
}

function normalizeTemplate(value) {
  return textValue(value)
    .toLowerCase()
    .replace(/https?:\/\/\S+|www\.\S+/g, " [pautan] ")
    .replace(/\b(?:rm\s*)?\d+(?:[.,]\d+)?\b/g, " [angka] ")
    .replace(/[^\p{L}\p{N}\[\]\s]+/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function binaryLabel(label) {
  const value = textValue(label).toLowerCase();
  return value.includes("kawalan") || value.includes("bukan penipuan") ? "control" : "risk";
}

function sortedUnique(values) {
  return [...new Set(values.map(textValue).filter(Boolean))].sort((a, b) => a.localeCompare(b, "ms"));
}

const speech = await SpreadsheetFile.importXlsx(await FileBlob.load(speechPath));
const emotion = await SpreadsheetFile.importXlsx(await FileBlob.load(emotionPath));
const move = await SpreadsheetFile.importXlsx(await FileBlob.load(movePath));

const sourceSpecs = [
  {
    workbook: speech,
    file: path.basename(speechPath),
    module: "ScamSpeech",
    sheet: "DATASET_UTAMA",
    levelField: "Tahap_Risiko",
    categoryField: "Jenis_Scam_Kawalan",
  },
  {
    workbook: emotion,
    file: path.basename(emotionPath),
    module: "ScamEmotion",
    sheet: "DATASET_UTAMA",
    levelField: "Tahap_Risiko_Emosi",
    categoryField: "Pencetus_Emosi",
  },
  {
    workbook: move,
    file: path.basename(movePath),
    module: "ScamMove",
    sheet: "DATASET_UTAMA",
    levelField: "Tahap_Risiko",
    categoryField: "Move_Dominan",
  },
  {
    workbook: move,
    file: path.basename(movePath),
    module: "ScamMove",
    sheet: "DATASET_KAWALAN",
    levelField: "Tahap_Risiko",
    categoryField: "Move_Dominan",
  },
];

const rawRecords = [];
for (const spec of sourceSpecs) {
  const rows = rowsFromSheet(spec.workbook, spec.sheet);
  rows.forEach((row, rowIndex) => {
    const text = textValue(row.Ayat_Ujaran);
    if (!text) return;
    rawRecords.push({
      source_file: spec.file,
      source_sheet: spec.sheet,
      source_row: rowIndex + 2,
      module: spec.module,
      text,
      template_text: normalizeTemplate(text),
      label: textValue(row.Label_Empirikal),
      binary_label: binaryLabel(row.Label_Empirikal),
      expected_level: textValue(row[spec.levelField]),
      expected_category: textValue(row[spec.categoryField]),
    });
  });
}

const exactGroups = new Map();
for (const row of rawRecords) {
  if (!exactGroups.has(row.text)) exactGroups.set(row.text, []);
  exactGroups.get(row.text).push(row);
}

const exactRecords = [...exactGroups.entries()]
  .map(([text, rows]) => {
    const binaryLabels = sortedUnique(rows.map((row) => row.binary_label));
    if (binaryLabels.length !== 1) {
      throw new Error(`Cross-label conflict for exact text: ${text}`);
    }
    return {
      text,
      template_text: rows[0].template_text,
      binary_label: binaryLabels[0],
      modules: sortedUnique(rows.map((row) => row.module)),
      source_sheets: sortedUnique(rows.map((row) => `${row.module}/${row.source_sheet}`)),
      original_labels: sortedUnique(rows.map((row) => row.label)),
      expected_levels: sortedUnique(rows.map((row) => row.expected_level)),
      expected_categories: sortedUnique(rows.map((row) => row.expected_category)),
      source_occurrences: rows.length,
    };
  })
  .sort((a, b) => a.binary_label.localeCompare(b.binary_label) || a.text.localeCompare(b.text, "ms"))
  .map((row, index) => ({
    record_id: `E${String(index + 1).padStart(3, "0")}`,
    ...row,
  }));

const groups = new Map();
for (const row of rawRecords) {
  const key = row.template_text;
  if (!groups.has(key)) groups.set(key, []);
  groups.get(key).push(row);
}

const templates = [...groups.entries()]
  .map(([templateText, rows]) => {
    const labels = sortedUnique(rows.map((row) => row.binary_label));
    if (labels.length !== 1) {
      throw new Error(`Cross-label conflict after template normalization: ${templateText}`);
    }
    const exactVariants = sortedUnique(rows.map((row) => row.text));
    const representative = [...exactVariants].sort((a, b) => a.length - b.length || a.localeCompare(b, "ms"))[0];
    return {
      template_text: templateText,
      representative_text: representative,
      binary_label: labels[0],
      modules: sortedUnique(rows.map((row) => row.module)),
      source_sheets: sortedUnique(rows.map((row) => `${row.module}/${row.source_sheet}`)),
      original_labels: sortedUnique(rows.map((row) => row.label)),
      expected_levels: sortedUnique(rows.map((row) => row.expected_level)),
      expected_categories: sortedUnique(rows.map((row) => row.expected_category)),
      source_occurrences: rows.length,
      exact_variant_count: exactVariants.length,
    };
  })
  .sort((a, b) => a.binary_label.localeCompare(b.binary_label) || a.template_text.localeCompare(b.template_text, "ms"))
  .map((row, index) => ({
    template_id: `T${String(index + 1).padStart(3, "0")}`,
    ...row,
  }));

const testSpecs = [
  {
    workbook: speech,
    module: "ScamSpeech",
    inputField: "Mesej Ujian",
    levelField: "Jangkaan Tahap Risiko",
    categoryField: "Jangkaan Jenis",
  },
  {
    workbook: emotion,
    module: "ScamEmotion",
    inputField: "Mesej Ujian",
    levelField: "Jangkaan Tahap",
    categoryField: "Jangkaan Kod 6E",
  },
  {
    workbook: move,
    module: "ScamMove",
    inputField: "Input_Ujian",
    levelField: "Jangkaan_Risiko",
    categoryField: "Move_Dijangka",
  },
];

const systemTests = testSpecs.flatMap((spec) =>
  rowsFromSheet(spec.workbook, "CONTOH_UJIAN_SISTEM").map((row, index) => ({
    test_id: `${spec.module}-${String(index + 1).padStart(2, "0")}`,
    module: spec.module,
    text: textValue(row[spec.inputField]),
    expected_level: textValue(row[spec.levelField]),
    expected_category: textValue(row[spec.categoryField]),
  })),
);

const countBy = (rows, field) => Object.fromEntries(
  [...new Set(rows.map((row) => row[field]))]
    .sort()
    .map((key) => [key, rows.filter((row) => row[field] === key).length]),
);

const payload = {
  schema_version: "1.1",
  generated_on: "2026-08-25",
  source_status: "synthetic_controlled_not_ground_truth",
  methodology_note:
    "All source rows were audited. Runtime matching uses one representative per normalized template so repeated synthetic variants do not receive extra weight.",
  statistics: {
    source_rows: rawRecords.length,
    exact_unique_messages: exactRecords.length,
    exact_unique_by_label: countBy(exactRecords, "binary_label"),
    exact_level_conflicts: exactRecords.filter((row) => row.expected_levels.length > 1).length,
    normalized_templates: templates.length,
    templates_by_label: countBy(templates, "binary_label"),
    system_tests: systemTests.length,
  },
  templates,
  exact_records: exactRecords,
  system_tests: systemTests,
};

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
console.log(JSON.stringify(payload.statistics, null, 2));
