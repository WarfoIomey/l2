<template>
  <div>
    <template v-if="!props.simpleMode">
      <div class="margin-first-item">
        <RadioFieldById
          v-if="currentFileTypes.length > 0"
          v-model="selectedType"
          :variants="currentFileTypes"
          @modified="changeType"
        />
        <h5
          v-else
          class="text-center"
        >
          Такие расширения файлов не поддерживаются
        </h5>
      </div>
      <div
        v-if="selectedType"
        class="margin-item"
      >
        <Treeselect
          v-if="currentFileForms.length > 0"
          v-model="selectedForm"
          :options="currentFileForms"
          placeholder="Выберите структуру файла"
        />
        <h5
          v-else-if="noSupportedFileForms"
          class="text-center"
        >
          Такие структуры файла не поддерживаются
        </h5>
        <h5
          v-else
          class="text-center"
        >
          Нет разрешенных форм
        </h5>
      </div>
      <div
        v-if="selectedForm"
        class="margin-item"
      >
        <input
          ref="fileInput"
          style="margin-top: 15px"
          type="file"
          class="form-control-file"
          :accept="fileFilter"
          @change="handleFileUpload"
        >
      </div>
      <div
        v-if="fileIsSelected"
        class="margin-item"
      >
        <button
          class="btn btn-blue-nb"
          @click="submitFileUpload()"
        >
          Загрузить файл
        </button>
      </div>
    </template>
    <template v-if="props.simpleMode">
      <div class="simple">
        <slot name="simple-label">
          <label class="simple-label">Загрузка файла</label>
        </slot>
        <input
          ref="fileInput"
          type="file"
          class="form-control-file"
          :accept="fileFilter"
          @change="handleFileUpload"
        >
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
// todo - slot на вывод результата, для удобного вывода каждому)
// todo - дефолтный вывод результата - таблица, строчка
import {
  getCurrentInstance, onMounted, PropType, ref, watch,
} from 'vue';
import Treeselect from '@riophae/vue-treeselect';

import '@riophae/vue-treeselect/dist/vue-treeselect.css';
import RadioFieldById from '@/fields/RadioFieldById.vue';
import { useStore } from '@/store';
import * as actions from '@/store/action-types';
import api from '@/api';

import typesAndForms, { formsFile, typesFile } from './types-and-forms-file';

const {
  getTypes, getForms, getFileFilters, unsupportedFileForms,
} = typesAndForms();

const store = useStore();

const root = getCurrentInstance().proxy.$root;
const props = defineProps({
  typesFile: {
    type: Array as PropType<string[]>,
    required: false,
  },
  formsFile: {
    type: Array as PropType<string[]>,
    required: false,
  },
  uploadResult: {
    type: Boolean,
    required: false,
  },
  entityId: {
    type: Number,
    required: false,
  },
  otherNeedData: {
    type: Object || Array || String || Number,
    required: false,
  },
  simpleMode: {
    type: Boolean,
    required: false,
  },
});

const emit = defineEmits(['uploadSuccess']);

const fileFilter = ref('');

const currentFileTypes = ref<typesFile[]>([]);
const selectedType = ref(null);

const allowedForms = ref([]);
const currentFileForms = ref<formsFile[]>([]);
const selectedForm = ref(null);

const allowedFormsForOrganization = async () => {
  await store.dispatch(actions.INC_LOADING);
  const { result } = await api('parse-file/get-allowed-forms');
  await store.dispatch(actions.DEC_LOADING);
  allowedForms.value = result;
};

const noSupportedFileForms = ref(false);

onMounted(async () => {
  await allowedFormsForOrganization();
  currentFileTypes.value = getTypes(props.typesFile);
  if (props.simpleMode && currentFileTypes.value.length > 0) {
    selectedType.value = currentFileTypes.value[0].id;
  }
});

const changeType = () => {
  fileFilter.value = getFileFilters(selectedType.value);
  currentFileForms.value = getForms(
    String(selectedType.value),
    props.formsFile,
    props.uploadResult,
    allowedForms.value,
  );
  if (currentFileForms.value.length > 0) {
    selectedForm.value = currentFileForms.value[0].id;
  } else {
    selectedForm.value = null;
  }
  noSupportedFileForms.value = unsupportedFileForms(selectedType.value, props.formsFile);
};

watch(selectedType, () => {
  if (props.simpleMode) {
    changeType();
  }
});

const fileInput = ref(null);
const file = ref(null);
const fileIsSelected = ref(false);
const clearFile = () => {
  file.value = null;
  const input = fileInput.value as HTMLInputElement;
  input.value = '';
  fileIsSelected.value = false;
};

const submitFileUpload = async () => {
  try {
    const formData = new FormData();
    formData.append('file', file.value);
    formData.append('selectedForm', selectedForm.value);
    formData.append('entityId', props.entityId ? String(props.entityId) : null);
    formData.append('otherNeedData', props.otherNeedData ? props.otherNeedData : null);
    await store.dispatch(actions.INC_LOADING);
    const { ok, message } = await api('parse-file/upload-file', null, null, null, formData);
    await store.dispatch(actions.DEC_LOADING);
    if (ok) {
      root.$emit('msg', 'ok', 'Файл загружен');
      emit('uploadSuccess');
    } else {
      root.$emit('msg', 'error', message);
    }
    clearFile();
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error(e);
    root.$emit('msg', 'error', 'Ошибка загрузки');
  }
};

watch(file, () => {
  if (props.simpleMode && file.value) {
    submitFileUpload();
  }
});

const handleFileUpload = () => {
  const input = fileInput.value as HTMLInputElement;
  const re = /(?:\.([^.]+))?$/;
  const fileExtension = re.exec(input.value)[1];
  if (fileFilter.value.includes(fileExtension.toLowerCase())) {
    [file.value] = input.files;
    fileIsSelected.value = true;
  } else {
    input.value = '';
    fileIsSelected.value = false;
    root.$emit('msg', 'error', `Файл не ${selectedType.value}`);
  }
};

</script>

<style scoped lang="scss">
.margin-first-item {
  margin-bottom: 10px
}
.margin-item {
  margin: 10px 0;
}
.simple {
  margin-bottom: 2px;
}
.simple-label {
  margin-bottom: 0;
}
</style>
