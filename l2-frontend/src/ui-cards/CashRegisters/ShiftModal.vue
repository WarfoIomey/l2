<template>
  <Modal
    show-footer="true"
    ignore-body
    white-bg="true"
    max-width="710px"
    width="100%"
    margin-left-right="auto"
    @close="closeModal"
  >
    <span
      v-if="!loading"
      slot="header"
    >{{ 'Кассовые смены' }}</span>
    <span
      v-if="loading"
      slot="header"
      class="text-center"
    >{{ 'Загрузка...' }}</span>
    <div slot="body">
      <div class="body">
        <div
          v-if="!shiftIsOpen"
          class="flex"
        >
          <div class="input-group">
            <span
              class="input-group-addon nbr width-title"
            >Касса</span>
            <Treeselect
              v-model="selectedCashRegister"
              :options="cashRegisters"
              :disabled="shiftIsOpen || loading || statusShift === 'Смена закрывается'"
              placeholder="Выберите кассу"
            />
          </div>
          <button
            class="btn btn-blue-nb nbr width-action"
            :disabled="!selectedCashRegister || loading || statusShift === 'Смена открывается'"
            @click="openShift"
          >
            Открыть
          </button>
        </div>
        <div v-if="shiftIsOpen">
          <table class="table">
            <colgroup>
              <col style="width: 50px">
              <col style="width: 50px">
              <col>
              <col style="width: 100px">
              <col style="width: 100px">
              <col style="width: 100px">
            </colgroup>
            <thead>
              <tr>
                <th class="text-center">
                  <strong>Смена №</strong>
                </th>
                <th class="text-center">
                  <strong>Касса №</strong>
                </th>
                <th class="text-center">
                  <strong>Название кассы</strong>
                </th>
                <th class="text-center">
                  <strong>Открыта</strong>
                </th>
                <th class="text-center">
                  <strong>Статус</strong>
                </th>
                <th />
              </tr>
            </thead>
            <tr>
              <td class="text-center">
                {{ currentShiftData.shiftId }}
              </td>
              <td class="text-center">
                {{ currentShiftData.cashRegisterId }}
              </td>
              <VueTippyTd
                :text="currentShiftData.cashRegisterTitle"
                class="cash-register-title"
              />
              <td class="text-center">
                {{ currentShiftData.open_at }}
              </td>
              <td class="text-center">
                {{ currentShiftData.status }}
              </td>
              <td>
                <div class="button">
                  <button
                    v-tippy
                    class="btn btn-blue-nb nbr close-button"
                    title="Закрыть смену"
                    :disabled="!shiftIsOpen || statusShift === 'Смена закрывается'"
                    @click="closeShift"
                  >
                    <i class="fa fa-times" />
                  </button>
                </div>
              </td>
            </tr>
          </table>
        </div>
      </div>
    </div>
    <div slot="footer">
      <div class="row">
        <div class="col-xs-4">
          <button
            class="btn btn-primary-nb btn-blue-nb"
            type="button"
            @click="closeModal"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">

import {
  computed, getCurrentInstance, onMounted, ref,
} from 'vue';
import Treeselect from '@riophae/vue-treeselect';

import * as actions from '@/store/action-types';
import Modal from '@/ui-cards/Modal.vue';
import '@riophae/vue-treeselect/dist/vue-treeselect.css';
import { useStore } from '@/store';
import api from '@/api';
import VueTippyTd from '@/construct/VueTippyTd.vue';

interface shiftData {
  shiftId: number,
  cashRegisterId: number,
  cashRegisterTitle: string,
  open_at: string,
  status: string
}

const store = useStore();
const root = getCurrentInstance().proxy.$root;
const emit = defineEmits(['closeModal']);

const loading = ref(false);

const cashRegister = computed(() => store.getters.cashRegisterShift);
const shiftIsOpen = computed(() => !!cashRegister.value?.cashRegisterId);
const selectedCashRegister = ref(null);
const cashRegisters = ref([]);
const currentShiftData = ref<shiftData>({
  shiftId: null,
  cashRegisterId: null,
  cashRegisterTitle: '',
  open_at: '',
  status: '',
});
const statusShift = ref('');

// eslint-disable-next-line @typescript-eslint/no-unused-vars
let intervalReq = null;

const getCashRegisters = async () => {
  await store.dispatch(actions.INC_LOADING);
  const { result } = await api('cash-register/get-cash-registers');
  await store.dispatch(actions.DEC_LOADING);
  cashRegisters.value = result;
};
const getShiftData = async () => {
  const { ok, message, data } = await api('cash-register/get-shift-data');
  if (ok) {
    currentShiftData.value = data;
    statusShift.value = data.status;
    if (!shiftIsOpen.value && data.status === 'Открывается') {
      intervalReq = setTimeout(() => getShiftData(), 1000);
    } else if (!shiftIsOpen.value && data.status === 'Открыта') {
      await store.dispatch(actions.OPEN_SHIFT, { cashRegisterId: data.cashRegisterId, shiftId: data.shiftId });
      root.$emit('msg', 'ok', 'Смена открыта');
      intervalReq = null;
    } else if (shiftIsOpen.value && data.status === 'Закрывается') {
      intervalReq = setTimeout(() => getShiftData(), 1000);
    } else if (shiftIsOpen.value && data.status === 'Закрыта') {
      await store.dispatch(actions.CLOSE_SHIFT);
      root.$emit('msg', 'ok', 'Смена закрыта');
      intervalReq = null;
    }
  } else {
    selectedCashRegister.value = null;
    intervalReq = null;
    root.$emit('msg', 'error', message);
  }
};

onMounted(async () => {
  await getCashRegisters();
  selectedCashRegister.value = shiftIsOpen.value ? cashRegister.value.cashRegisterId : null;
  await getShiftData();
});

const closeModal = () => {
  emit('closeModal');
};

const openShift = async () => {
  if (!selectedCashRegister.value) {
    root.$emit('msg', 'error', 'Касса не выбрана');
  } else {
    loading.value = true;
    const { ok, message } = await api('cash-register/open-shift', { cashRegisterId: selectedCashRegister.value });
    loading.value = false;
    if (ok) {
      root.$emit('msg', 'ok', 'Заявка отправлена');
      await getShiftData();
    } else {
      root.$emit('msg', 'error', message);
    }
  }
};
const closeShift = async () => {
  loading.value = true;
  const { ok, message } = await api('cash-register/close-shift', { cashRegisterId: selectedCashRegister.value });
  loading.value = false;
  if (ok) {
    await getShiftData();
  } else {
    root.$emit('msg', 'error', message);
  }
};

</script>

<style scoped lang="scss">
.pointer {
  cursor: pointer;
}
.body {
  height: 300px;
}
.flex {
  display: flex;
}
.width-title {
  width: 100px;
}
.width-action {
  min-width: 100px;
}

::v-deep .vue-treeselect__control {
  border: 1px solid #AAB2BD !important;
  border-radius: 0;
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
  .btn {
    align-self: stretch;
    flex: 1;
    padding: 7px 0;
  }
.cash-register-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.close-button {
  padding: 9px 0;
}
</style>
