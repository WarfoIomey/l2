<template>
  <div
    class="root"
    :class="{ noGrid: !hasGrid, hasGrid }"
  >
    <div class="a">
      <PatientPicker
        v-model="selected_card"
        directive_from_need="true"
        search_results="true"
        :selected-researches="selected_researches"
        bottom_picker="true"
      >
        <div
          slot="for_card"
          class="text-right"
        >
          <div
            v-if="selected_researches.length > 0"
            style="margin-top: 5px; text-align: left"
          >
            <table class="table table-bordered lastresults">
              <colgroup>
                <col width="180">
                <col>
                <col width="110">
                <col width="110">
              </colgroup>
              <tbody>
                <LastResult
                  v-for="p in selected_researches"
                  :key="p"
                  :individual="selected_card.individual_pk"
                  :research="p"
                />
              </tbody>
            </table>
          </div>
        </div>
        <div
          v-if="selected_card.pk >= 0"
          slot="for_card_bottom"
          class="bottom-inner"
        >
          <!--<a href="#" @click.prevent="do_show_rmis_send_directions" v-if="selected_card.is_rmis">
            <span>Направить в другую МО</span>
          </a>-->
          <div class="dropup">
            <button
              class="btn btn-blue-nb btn-ell dropdown-toggle"
              type="button"
              data-toggle="dropdown"
              style="text-align: right !important; border-radius: 0; width: 100%"
            >
              Печатные формы <span class="caret" />
            </button>
            <ul class="dropdown-menu">
              <li
                v-for="f in forms"
                :key="`${f.url || '#'}_${f.title}`"
                :class="f.isGroup && 'dropdown-submenu'"
              >
                <a
                  :href="f.url || '#'"
                  :target="!f.isGroup && '_blank'"
                  class="ddm"
                >{{ f.title }}</a>
                <ul
                  v-if="f.isGroup"
                  class="dropdown-menu multi-level"
                >
                  <li
                    v-for="ff in f.forms"
                    :key="ff.url"
                  >
                    <a
                      :href="ff.url"
                      target="_blank"
                      class="ddm"
                    >{{ ff.title }}</a>
                  </li>
                </ul>
              </li>
            </ul>
          </div>
          <a
            v-if="selected_card.is_rmis"
            href="#"
            class="a-under"
            @click.prevent="do_show_rmis_directions"
          >
            <span>Направления из РМИС</span>
          </a>
          <a
            class="a-under"
            :href="report_url"
          >
            <span>Отчёт по результатам</span>
          </a>

          <router-link
            v-if="can_create_tickets"
            :to="ticket_url"
            class="a-under"
          >
            <span>Создать статталон</span>
          </router-link>
        </div>
      </PatientPicker>
    </div>
    <div class="b gutter gutter-col gutter-column-1" />
    <div
      v-if="!l2_only_doc_call"
      class="c"
    >
      <DirectionsHistory
        :patient_pk="selected_card.pk"
        :days-subtract="daysSubtract"
      />
    </div>
    <div
      v-else-if="!hasGrid"
      class="c"
    >
      <div />
    </div>
    <div
      class="d gutter gutter-row gutter-row-1"
      :class="{ onlyDocCall: l2_only_doc_call }"
    />
    <div class="e">
      <ResearchesPicker v-model="selected_researches" />
    </div>
    <div class="f gutter gutter-col gutter-column-2" />
    <div
      class="g"
      :class="{ noMoreModules: !l2_doc_call && !l2_list_wait && !rmis_queue && !l2_schedule,
                onlyDocCall: l2_only_doc_call }"
    >
      <DirectAndPlanSwitcher
        v-if="(l2_doc_call || l2_list_wait || rmis_queue || l2_schedule) && !l2_only_doc_call"
        v-model="mode"
        :bages="modes_counts"
      />
      <div
        v-show="mode === DIRECTION_MODE_DIRECTION"
        v-if="!l2_only_doc_call"
        :style="(l2_doc_call || l2_list_wait || rmis_queue || l2_schedule) && 'border-top: 1px solid #434a54'"
      >
        <SelectedResearches
          :operator="selected_card.operator"
          :ofname="selected_card.ofname"
          :visible="mode === DIRECTION_MODE_DIRECTION"
          :main_diagnosis="selected_card.main_diagnosis"
          :history_num="selected_card.history_num"
          :valid="patient_valid"
          :researches="selected_researches"
          :base="selected_card.base"
          :card_pk="selected_card.pk"
          :selected_card="selected_card"
        />
      </div>
      <div
        v-show="mode === DIRECTION_MODE_CALL"
        v-if="l2_doc_call"
      >
        <CallDoctor
          :card_pk="selected_card.pk"
          :researches="selected_researches"
          :visible="mode === DIRECTION_MODE_CALL"
        />
      </div>
      <div
        v-show="mode === DIRECTION_MODE_WAIT"
        v-if="l2_list_wait && !l2_only_doc_call"
      >
        <ListWaitCreator
          :card_pk="selected_card.pk"
          :researches="selected_researches"
          :visible="mode === DIRECTION_MODE_WAIT"
        />
      </div>
      <div
        v-if="(rmis_queue && !l2_only_doc_call && mode === DIRECTION_MODE_ECP_REGISTRATION) ||
          (l2_schedule && mode === DIRECTION_MODE_ECP_REGISTRATION)"
      >
        <div
          v-if="selected_card.pk"
          class="schedule-root"
        >
          <ServiceScheduleEcp
            v-for="r in selected_researches"
            :key="r"
            :service-pk="r"
            :card-id="selected_card.pk"
          />
        </div>
      </div>
    </div>
    <ResultsViewer
      v-if="show_results_pk > -1"
      :pk="show_results_pk"
    />
    <RmisDirectionsViewer
      v-if="show_rmis_directions && selected_card.is_rmis"
      :card="selected_card"
    />
  </div>
</template>

<script lang="ts">
import Split from 'split-grid';

import ResearchesPicker from '@/ui-cards/ResearchesPicker.vue';
import PatientPicker from '@/ui-cards/PatientPicker.vue';
import SelectedResearches from '@/ui-cards/SelectedResearches.vue';
import DirectionsHistory from '@/ui-cards/DirectionsHistory/index.vue';
import ResultsViewer from '@/modals/ResultsViewer.vue';
import RmisDirectionsViewer from '@/modals/RmisDirectionsViewer.vue';
import LastResult from '@/ui-cards/LastResult.vue';
import DirectAndPlanSwitcher from '@/ui-cards/DirectAndPlanSwitcher.vue';
import ServiceScheduleEcp from '@/ui-cards/ServiceScheduleEcp.vue';
import forms from '@/forms';
import {
  DIRECTION_MODE_CALL,
  DIRECTION_MODE_DIRECTION,
  DIRECTION_MODE_ECP_REGISTRATION,
  DIRECTION_MODE_WAIT,
} from '@/constants';
import CallDoctor from '@/ui-cards/CallDoctor.vue';
import ListWaitCreator from '@/ui-cards/ListWaitCreator.vue';
import { valuesToString } from '@/utils';

export default {
  name: 'Directions',
  components: {
    ListWaitCreator,
    CallDoctor,
    DirectAndPlanSwitcher,
    PatientPicker,
    ResearchesPicker,
    SelectedResearches,
    DirectionsHistory,
    ResultsViewer,
    RmisDirectionsViewer,
    LastResult,
    ServiceScheduleEcp,
  },
  async beforeRouteLeave(to, from, next) {
    const msg = this.unload();

    if (msg) {
      try {
        await this.$dialog.confirm(msg);
      } catch (_) {
        next(false);
        return;
      }
    }

    next();
  },
  data() {
    return {
      selected_card: {
        pk: -1,
        base: {},
        ofname: -1,
        ofname_dep: -1,
        individual_pk: -1,
        operator: false,
        is_rmis: false,
        history_num: '',
        family: '',
        name: '',
        twoname: '',
        birthday: '',
        age: '',
        main_diagnosis: '',
      },
      selected_researches: [],
      show_results_pk: -1,
      show_rmis_directions: false,
      show_rmis_send_directions: false,
      diagnos: '',
      fin: -1,
      hasGrid: window.Modernizr.cssgrid,
      mode: DIRECTION_MODE_DIRECTION,
      DIRECTION_MODE_DIRECTION,
      DIRECTION_MODE_CALL,
      DIRECTION_MODE_WAIT,
      DIRECTION_MODE_ECP_REGISTRATION,
      modes_counts: {
        [DIRECTION_MODE_CALL]: 0,
        [DIRECTION_MODE_WAIT]: 0,
      },
      disabled_forms: [],
    };
  },
  computed: {
    forms() {
      return this.makeForms(forms);
    },
    patient_valid() {
      return this.selected_card.pk !== -1;
    },
    ticket_url() {
      return {
        name: 'statistics-tickets',
        query: {
          base_pk: this.selected_card.base.pk,
          card_pk: this.selected_card.pk,
          ofname: this.selected_card.ofname,
          ofname_dep: this.selected_card.ofname_dep,
        },
      };
    },
    report_url() {
      // eslint-disable-next-line max-len
      return `/mainmenu/results_report?individual_pk=${this.selected_card.individual_pk}&base_pk=${this.selected_card.base.pk}&card_pk=${this.selected_card.pk}`;
    },
    can_create_tickets() {
      if ('groups' in this.$store.getters.user_data) {
        for (const g of this.$store.getters.user_data.groups) {
          if (g === 'Оформление статталонов' || g === 'Лечащий врач' || g === 'Оператор лечащего врача') {
            return true;
          }
        }
      }
      return false;
    },
    l2_list_wait() {
      return this.$store.getters.modules.l2_list_wait;
    },
    l2_doc_call() {
      return this.$store.getters.modules.l2_doc_call;
    },
    l2_only_doc_call() {
      return this.$store.getters.modules.l2_only_doc_call && this.l2_doc_call;
    },
    rmis_queue() {
      return this.$store.getters.modules.l2_rmis_queue;
    },
    l2_schedule() {
      return this.$store.getters.modules.l2_schedule;
    },
    daysSubtract() {
      return this.$store.getters.modules.days_subtract;
    },
  },
  watch: {
    l2_only_doc_call: {
      handler() {
        if (this.l2_only_doc_call) {
          this.mode = DIRECTION_MODE_CALL;
        }
      },
      immediate: true,
    },
  },
  created() {
    this.$root.$on('show_results', (pk) => {
      this.show_results_pk = pk;
    });

    this.$root.$on('hide_results', () => {
      this.show_results_pk = -1;
    });

    this.$root.$on('hide_rmis_directions', () => {
      this.show_rmis_directions = false;
      this.show_rmis_send_directions = false;
    });

    this.$root.$on('update_diagnos', (diagnos) => {
      this.diagnos = diagnos;
    });

    this.$root.$on('update_fin', (fin) => {
      this.fin = fin;
    });

    this.$root.$on('call-doctor:rows-count', (count) => {
      this.modes_counts[DIRECTION_MODE_CALL] = count;
    });

    this.$root.$on('list-wait-creator:rows-count', (count) => {
      this.modes_counts[DIRECTION_MODE_WAIT] = count;
    });
  },
  mounted() {
    if (this.hasGrid) {
      Split({
        columnGutters: [
          {
            track: 1,
            element: document.querySelector('.gutter-column-1'),
          },
          {
            track: 1,
            element: document.querySelector('.gutter-column-2'),
          },
        ],
        rowGutters: [
          {
            track: 1,
            element: document.querySelector('.gutter-row-1'),
          },
        ],
        minSize: 200,
      });
    }
    window.$(window).on('beforeunload', this.unload);
    this.get_disabled_forms();
  },
  beforeDestroy() {
    window.$(window).off('beforeunload', this.unload);
  },
  methods: {
    async get_disabled_forms() {
      const resultData = await this.$api('disabled-forms');
      this.disabled_forms = resultData.rows;
    },
    unload() {
      if (
        this.selected_card.pk === -1
        || this.selected_researches.length <= 0
        // @ts-ignore
        || document.activeElement?.href?.startsWith('sip:')
      ) {
        if (document.activeElement) {
          window.$(document.activeElement).blur();
        }
        return undefined;
      }

      return 'Исследования выбраны, но направления не созданы. Вы уверены, что хотите покинуть страницу?';
    },
    do_show_rmis_directions() {
      this.show_rmis_directions = true;
    },
    do_show_rmis_send_directions() {
      this.show_rmis_send_directions = true;
    },
    makeForms(formsBase) {
      return formsBase
        .map((f) => {
          if (f.isGroup) {
            return {
              ...f,
              forms: this.makeForms(f.forms),
            };
          }
          return {
            ...f,
            url: valuesToString(f.url, {
              card: this.selected_card.pk,
              individual: this.selected_card.individual_pk,
            }),
          };
        })
        .filter((f) => (this.selected_card.base.internal_type || f.not_internal) && !this.disabled_forms.includes(f.type));
    },
  },
};
</script>

<style scoped lang="scss">
.noGrid .gutter {
  display: none;
}

.noGrid {
  // FALLBACK FROM CSS GRID TO FLEXBOX START

  display: flex;
  flex-wrap: wrap;
  flex-direction: row;

  justify-items: stretch;
  align-items: stretch;

  & > div {
    flex-basis: 50%;
  }

  // FALLBACK FROM CSS GRID TO FLEXBOX END
}

.root {
  position: absolute;
  top: 36px;
  left: 0;
  right: 0;
  bottom: 0;

  &.hasGrid {
    display: grid;
    grid-template-columns: 1fr 5px 1fr;
    grid-template-rows: 1fr 5px 1fr;
    gap: 0;
    height: calc(calc(100vh - calc(100vh - 100%)) - 36px);
  }

  .a {
    grid-area: 1 / 1 / 2 / 2;

    padding-right: 0;
    padding-bottom: 0;
    text-align: left;
    background: #fff;
  }

  .b {
    grid-area: 1 / 2 / 2 / 3;
    display: block;
  }

  .c {
    grid-area: 1 / 3 / 2 / 4;

    padding-left: 0;
    padding-bottom: 0;
    text-align: left;
    background: #fff;
  }

  .d {
    grid-area: 2 / 1 / 3 / 4;
    display: block;
  }

  .e {
    grid-area: 3 / 1 / 4 / 2;

    padding-top: 0;
    padding-right: 0;
    text-align: left;
    background: #fff;
  }

  .f {
    grid-area: 3 / 2 / 4 / 3;
    display: block;
  }

  .g {
    grid-area: 3 / 3 / 4 / 4;

    &.onlyDocCall {
      grid-area: 1 / 3 / 4 / 4;
    }

    &:not(.onlyDocCall) {
      padding-top: 0;
    }

    padding-left: 0;
    text-align: left;
    background: #fff;
  }

  @media (max-width: 760px) {
    grid-template-columns: 1fr !important;
    grid-template-rows: repeat(4, 320px) !important;
    gap: 5px !important;

    & > div {
      padding: 5px !important;
    }

    .a {
      grid-area: 1 / 1 / 2 / 2;
    }

    .b {
      display: none;
    }

    .c {
      grid-area: 2 / 1 / 3 / 2;
    }

    .d {
      display: none;
    }

    .e {
      grid-area: 3 / 1 / 4 / 2;
    }

    .f {
      display: none;
    }

    .g {
      grid-area: 4 / 1 / 5 / 2;
    }
  }

  & > div {
    padding: 5px;

    & > div {
      border: 1px solid #aab2bd;
      position: relative;
    }
  }
}

#right_top {
  overflow: visible !important;
}

.lastresults {
  table-layout: fixed;
  padding: 0;
  margin: 0;
  color: #000;
  background-color: #ffdb4d;
  border-color: #000;

  ::v-deep th,
  ::v-deep td {
    border-color: #000;
  }

  ::v-deep a {
    color: #000;
    text-decoration: dotted underline;
  }

  ::v-deep a:hover {
    text-decoration: none;
  }
}

.fli {
  text-decoration: underline;
  margin-left: 5px;
}

.fli:hover {
  text-decoration: none;
}

.hasGrid {
  .gutter-col {
    cursor: col-resize;
    position: relative;
    padding: 0 !important;
    width: 5px;

    &::after {
      position: absolute;
      height: 10px;
      width: 1px;
      background-color: gray;
      top: calc(50% - 5px);
      left: 2px;

      content: ' ';
    }
  }

  .gutter-row {
    cursor: row-resize;
    position: relative;
    padding: 0 !important;
    height: 5px;

    &::before {
      position: absolute;
      height: 1px;
      width: 10px;
      background-color: gray;
      top: 2px;
      left: calc(25% - 5px);

      content: ' ';
    }

    &:not(.onlyDocCall)::after {
      position: absolute;
      height: 1px;
      width: 10px;
      background-color: gray;
      top: 2px;
      right: calc(25% - 5px);

      content: ' ';
    }
  }
}

.g {
  display: flex;
  flex-direction: column;
  justify-content: stretch;

  &:not(.noMoreModules) {
    > div:first-child {
      height: 34px;
      flex: 1 1 34px;
      width: 100%;
    }

    > div:not(:first-child) {
      flex: 1 calc(100% - 34px);
      height: calc(100% - 34px);
      width: 100%;
    }

    &:not(.onlyDocCall) {
      > div:first-child {
        border: none !important;
      }

      > div:not(:first-child) {
        border-top: none;
      }
    }
  }

  &.noMoreModules {
    > div:first-child {
      flex: 1 100%;
      height: 100%;
      width: 100%;
    }
  }
}

.schedule-root {
  padding: 10px;
  position: absolute;
  top: 0 !important;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: auto;

  & > ::v-deep div {
    margin-bottom: 15px;
  }
}
</style>
