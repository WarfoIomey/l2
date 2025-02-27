<template>
  <div>
    <Treeselect
      v-model="selectedComplex"
      :options="complexs"
      class="margin-bottom"
      value-format="object"
      placeholder="Выберите комплексную услугу"
    />
    <div class="block">
      <div class="flex">
        <input
          v-model="complexTitle"
          class="form-control nbr left-radius complex-title"
          :class="complexIsHidden ? 'hide-background hide-border' : ''"
          :disabled="complexIsHidden"
        >
        <div class="flex">
          <button
            v-if="complexIsSelected"
            v-tippy
            class="btn last btn-blue-nb nbr hidden-button"
            :title="complexIsHidden ? 'Показать': 'Скрыть'"
            @click="changeComplexHidden"
          >
            <i :class="complexIsHidden ? 'fa fa-eye' : 'fa fa-times'" />
          </button>
        </div>
        <div
          v-if="!complexIsHidden"
          class="flex"
        >
          <button
            class="btn btn-blue-nb nbr right-radius save-button"
            :class="complexIsSelected ? 'btn-border-left' : '' "
            @click="updateComplex"
          >
            {{ complexIsSelected ? 'Сохранить' : 'Создать' }}
          </button>
        </div>
      </div>
    </div>
    <div
      v-if="complexIsSelected"
      class="block"
    >
      <input
        v-model="search"
        class="form-control left-radius right-radius"
      >
    </div>
    <div
      v-if="complexIsSelected"
      class="block nbr"
    >
      <div class="scroll">
        <table class="table">
          <colgroup>
            <col>
            <col
              v-if="!complexIsHidden"
              width="35"
            >
          </colgroup>
          <tr
            v-for="service in filteredService"
            :key="service.id"
            class="tr-border"
          >
            <VueTippyTd
              class="service-padding"
              :class="service.hide ? 'hide-background' : '' "
              :text="service.label"
            />
            <td
              v-if="!complexIsHidden"
            >
              <div class="button">
                <button
                  v-tippy
                  class="btn btn-blue-nb nbr hidden-button"
                  :title="service.hide ? 'Показать' : 'Скрыть'"
                  @click="changeServiceHidden(service.id)"
                >
                  <i :class="service.hide ?'fa fa-eye' : 'fa fa-times'" />
                </button>
              </div>
            </td>
          </tr>
          <tr
            v-if="filteredService.length === 0"
            class="text-center empty-list"
          >
            <td>
              Нет данных
            </td>
          </tr>
        </table>
      </div>
    </div>
    <div
      v-if="complexIsSelected && !complexIsHidden"
      class="block"
    >
      <div class="flex">
        <Treeselect
          v-model="selectedService"
          :options="services"
          :disable-branch-nodes="true"
          class="add-treeselect"
          placeholder="Выберите услугу..."
        />
        <div class="flex">
          <button
            v-tippy
            class="btn btn-blue-nb nbr save-button right-radius"
            title="Добавить услугу"
            :disabled="!selectedService"
            @click="addService"
          >
            Добавить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  computed, getCurrentInstance, onMounted, ref, watch,
} from 'vue';
import Treeselect from '@riophae/vue-treeselect';

import '@riophae/vue-treeselect/dist/vue-treeselect.css';
import * as actions from '@/store/action-types';
import { useStore } from '@/store';
import api from '@/api';
import VueTippyTd from '@/construct/VueTippyTd.vue';

const store = useStore();
const root = getCurrentInstance().proxy.$root;

const selectedComplex = ref(null);
const complexs = ref([]);
const hiddenStatus = ref(false);
const complexTitle = ref('');

const complexIsHidden = computed(() => hiddenStatus.value);
const complexIsSelected = computed(() => selectedComplex.value);

const getComplexes = async () => {
  await store.dispatch(actions.INC_LOADING);
  const { result } = await api('construct/complex/get-complexes');
  await store.dispatch(actions.DEC_LOADING);
  complexs.value = result;
};

onMounted(() => {
  getComplexes();
});

const services = ref([]);
const selectedService = ref(null);
const getServices = async () => {
  await store.dispatch(actions.INC_LOADING);
  const { data } = await api('get-research-list');
  await store.dispatch(actions.DEC_LOADING);
  services.value = data;
};

const search = ref('');

interface serviceInComplex {
  id: string,
  label: string,
  hide: boolean,
}

const servicesInComplex = ref<serviceInComplex[]>([]);

const getServicesInComplex = async () => {
  await store.dispatch(actions.INC_LOADING);
  const { result } = await api('construct/complex/get-services', { complexId: selectedComplex.value.id });
  await store.dispatch(actions.DEC_LOADING);
  servicesInComplex.value = result;
};

const filteredService = computed(() => servicesInComplex.value.filter(service => {
  const serviceTitle = service.label.toLowerCase();
  const searchTerm = search.value.toLowerCase();
  return serviceTitle.includes(searchTerm);
}));

const checkHidden = async () => {
  await store.dispatch(actions.INC_LOADING);
  const { result } = await api('construct/complex/check-hidden', { complexId: selectedComplex.value.id });
  await store.dispatch(actions.DEC_LOADING);
  hiddenStatus.value = result;
};

const changeComplexHidden = async () => {
  await store.dispatch(actions.INC_LOADING);
  const { ok } = await api('construct/complex/change-complex-hidden', { complexId: selectedComplex.value.id });
  await store.dispatch(actions.DEC_LOADING);
  if (ok) {
    root.$emit('msg', 'ok', 'Успешно');
    hiddenStatus.value = !hiddenStatus.value;
  } else {
    root.$emit('msg', 'error', 'Ошибка');
  }
};

const updateComplex = async () => {
  if (!complexIsHidden.value) {
    await store.dispatch(actions.INC_LOADING);
    const { ok, id } = await api('construct/complex/update-complex', {
      complexId: complexIsSelected.value ? selectedComplex.value.id : null,
      complexTitle: complexTitle.value,
    });
    await store.dispatch(actions.DEC_LOADING);
    if (ok) {
      await getComplexes();
      if (!complexIsSelected.value) {
        selectedComplex.value = { id, label: complexTitle };
      }
      await getServices();
      root.$emit('msg', 'ok', 'Обновлено');
    } else {
      root.$emit('msg', 'error', 'Ошибка');
    }
  } else {
    root.$emit('msg', 'error', 'Нельзя редактировать скрытый комплекс');
  }
};

const changeServiceHidden = async (serviceId: number | string) => {
  await store.dispatch(actions.INC_LOADING);
  const { ok } = await api('construct/complex/change-service-hidden', {
    complexId: selectedComplex.value.id,
    serviceId,
  });
  await store.dispatch(actions.DEC_LOADING);
  if (ok) {
    await getServicesInComplex();
    root.$emit('msg', 'ok', 'Успешно');
  } else {
    root.$emit('msg', 'error', 'Ошибка');
  }
};

watch(selectedComplex, () => {
  if (complexIsSelected.value) {
    checkHidden();
    getServicesInComplex();
    complexTitle.value = selectedComplex.value.label;
  } else {
    servicesInComplex.value = [];
    complexTitle.value = '';
    hiddenStatus.value = false;
    selectedComplex.value = null;
  }
});

const addService = async () => {
  const serviceExists = servicesInComplex.value.find((service) => service.id === selectedService.value);
  if (!serviceExists && selectedService.value !== selectedComplex.value.id) {
    await store.dispatch(actions.INC_LOADING);
    const { ok, message } = await api('construct/complex/add-service', {
      complexId: selectedComplex.value.id,
      serviceId: selectedService.value,
    });
    await store.dispatch(actions.DEC_LOADING);
    if (ok) {
      await getServicesInComplex();
      selectedService.value = null;
      root.$emit('msg', 'ok', 'Услуга добавлена');
    } else {
      root.$emit('msg', 'error', message);
    }
  } else if (serviceExists) {
    root.$emit('msg', 'error', 'Услуга уже добавлена');
  } else if (selectedService.value === selectedComplex.value.id) {
    root.$emit('msg', 'error', 'Нельзя добавить в комплекс этот же комплекс');
  }
};

onMounted(() => {
  getServices();
});

</script>

<style scoped lang="scss">
.block {
  background-color: #fff;
  border-radius: 5px;
  margin-bottom: 20px;
}
.flex {
  display: flex;
}
.complex-title {
  padding: 17px 12px;
  border: 1px solid #ddd;
  flex-grow: 1;
}
.complex-title:focus {
  border: 1px solid #3bafda;
}
.margin-bottom {
  margin-bottom: 20px;
}
.scroll {
  min-height: 112px;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}
.table {
  margin-bottom: 0;
  table-layout: fixed;
}
.button {
  width: 100%;
  display: flex;
  flex-wrap: nowrap;
  flex-direction: row;
  justify-content: stretch;
}
.btn-flex {
  flex: 1;
}

.btn-border-left {
  border-left: 1px solid #ddd !important;
}
.right-radius {
  border-bottom-right-radius: 5px !important;
  border-top-right-radius: 5px !important;
}
.left-radius {
  border-bottom-left-radius: 5px !important;
  border-top-left-radius: 5px !important;
}
.tr-border {
  border: 1px solid #ddd;
}
.service-padding {
  padding: 6px 0 6px 12px
}
.hidden-button {
  width: 35px;
  padding: 6px;
}
.save-button {
  flex: 1;
  width: 100px;
}
::v-deep .add-treeselect .vue-treeselect__control {
  border-radius: 5px 0 0 5px !important;
}
.hide-background {
  background-image: linear-gradient(#6c7a89, #56616c);
  color: #fff;
}
.hide-border {
  border: 0;
}
.empty-list {
  width: 85px;
  margin: 20px auto;
}
</style>
