import { ref } from 'vue';

export interface typesFile {
  id: string,
  label: string,
}
export interface formsFile {
  id: string,
  label: string,
}
export default function typesAndForms() {
  const fileTypes = ref({
    XLSX: { id: 'XLSX', label: 'XLSX' },
    PDF: { id: 'PDF', label: 'PDF' },
    CSV: { id: 'CSV', label: 'CSV' },
  });
  const getTypes = (types: string[]): typesFile[] => {
    let result: typesFile[] = [];
    if (types && types.length > 0) {
      for (const type of types) {
        result.push(fileTypes.value[type]);
      }
    } else {
      result = Object.values(fileTypes.value);
    }
    return result;
  };

  /* (101.01) - 101 номер файла, 01 - номер функции в файле для обработки загруженного файла (см. parseFile) */
  const fileForms = ref({
    XLSX: {
      101.01: { id: 101.01, label: '101.01' },
      101.02: { id: 101.02, label: '101.02' },
      101.03: { id: 101.03, label: '101.03' },
    },
    PDF: {
      101.04: { id: 101.04, label: '101.04' },
    },
    CSV: {
      101.05: { id: 101.05, label: '101.05' },
    },
  });
  const getForms = (type: string, forms: string[] = []): formsFile[] => {
    let result: formsFile[] = [];
    if (forms && forms.length > 0) {
      for (const form of forms) {
        result.push(fileForms.value[type][form]);
      }
    } else {
      result = Object.values(fileForms.value[type]);
    }
    return result;
  };
  return { getTypes, getForms };
}
