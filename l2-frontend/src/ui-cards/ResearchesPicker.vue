<template>
  <div style="height: 100%; width: 100%; position: relative">
    <div class="top-picker">
      <button
        v-if="types.length > 1"
        class="btn btn-blue-nb btn-ell dropdown-toggle bt1"
        type="button"
        data-toggle="dropdown"
      >
        <span class="caret" />
        {{ selected_type.title }}
        {{ researches_selected_in_type(selected_type.pk) }}
      </button>
      <ul
        v-if="types.length > 1"
        class="dropdown-menu"
        style="margin-top: 1px"
      >
        <li
          v-for="row in types"
          :key="row.pk"
        >
          <a
            href="#"
            @click.prevent="select_type(row.pk)"
          >{{ row.title }} {{ researches_selected_in_type(row.pk) }}</a>
        </li>
      </ul>
      <button
        v-if="types.length === 1"
        class="btn btn-blue-nb btn-ell"
        type="button"
        style="width: 135px; border-radius: 0"
      >
        {{ selected_type.title }}
      </button>
      <div
        class="top-inner"
        :class="departments_of_type.length > 7 ? 'top-inner-right' : '' "
      >
        <div
          v-if="l2_all_service"
          class="top-inner-select all-dep"
          :class="{ active: dep === 'all' }"
          @click="select_dep('all')"
        >
          <span> {{ 'Все' }}</span>
        </div>
        <div
          v-for="row in departments_of_type.slice(0, 7)"
          :key="row.pk"
          v-tippy="{ placement: 'bottom', arrow: true }"
          class="top-inner-select"
          :class="{ active: row.pk === dep }"
          :title="row.title"
          @click="select_dep(row.pk)"
        >
          <span>
            {{ row.title }}
            <span v-if="researches_selected_in_department(row.pk).length > 0">
              &nbsp;({{ researches_selected_in_department(row.pk).length }})
            </span>
          </span>
        </div>
      </div>
      <div class="btn-group depart-other">
        <button
          v-if="departments_of_type.length > 7"
          class="btn btn-blue-nb btn-ell dropdown-toggle depart-other depart-other-btn"
          type="button"
          data-toggle="dropdown"
        >
          <span class="caret" />
          {{ dep_i > 6 && dep !== 'all' ? departments_of_type[dep_i]?.title : 'Ещё' }}
        </button>
        <ul
          v-if="departments_of_type.length > 7"
          class="dropdown-menu depart-other-dropdown"
          style="margin-top: 1px"
        >
          <li
            v-for="row in departments_of_type.slice(7)"
            :key="row.pk"
          >
            <a
              href="#"
              @click.prevent="select_dep(row.pk)"
            >{{ row.title }}</a>
          </li>
        </ul>
      </div>
    </div>
    <div
      v-if="researches_display.length > 0"
      class="content-picker"
      :class="{ hidetemplates: hidetemplates && !just_search }"
    >
      <template v-if="work_as_subcategory">
        <template v-if="selectedSubcategory === -1">
          <div class="category-title">
            Категории
          </div>
          <CategoryPick
            v-for="row in subcategories"
            :key="row.pk"
            class="research-select"
            :category="row"
            @click.native="selectedSubcategory = row.pk"
          />
        </template>
        <template v-else>
          <div class="category-title">
            <a
              href="#"
              class="a-under"
              @click.prevent="selectedSubcategory = -1"
            > <i class="fa fa-arrow-left" /> Назад</a>&nbsp;&nbsp;{{ selectedSubcategoryObj.title }}
          </div>

          <ResearchPick
            v-for="row in selectedSubcategoryObj.researches || []"
            :key="row.pk"
            class="research-select"
            :class="{ active: research_selected(row.pk) }"
            :research="row"
            @click.native="select_research(row.pk)"
          />
        </template>
      </template>
      <template v-else>
        <ResearchPick
          v-for="row in researches_display"
          :key="row.pk"
          class="research-select"
          :class="[{ active: research_selected(row.pk) }, l2_research_col ? `research-select-col--${l2_research_col}` : '']"
          :research="row"
          @click.native="select_research(row.pk)"
        />
      </template>
    </div>
    <div
      v-else
      class="content-none"
    >
      Нет данных
    </div>
    <div
      v-if="!hidetemplates"
      class="bottom-picker"
      style="white-space: nowrap"
    >
      <div
        class="dropup"
        style="display: inline-block"
      >
        <button
          class="btn btn-blue-nb btn-ell dropdown-toggle"
          type="button"
          data-toggle="dropdown"
          style="text-align: left !important; border-radius: 0"
        >
          <span class="caret" />
          Загрузить шаблон
        </button>
        <ul class="dropdown-menu">
          <li
            v-for="row in templates"
            :key="row.pk"
          >
            <a
              href="#"
              @click.prevent="load_template(row.pk)"
            >{{ row.title }}</a>
          </li>
        </ul>
      </div>
      <div style="display: flex; width: calc(100% - 164px); justify-content: flex-end">
        <div
          v-show="founded_n !== '' && search !== ''"
          id="founded-n"
        >
          <div style="font-size: 16px">
            {{ founded_n }}
          </div>
        </div>
        <div style="position: relative; max-width: 335px; width: 100%; display: flex">
          <div
            v-if="founded_templates.length > 0"
            id="templates-tip"
          >
            <div
              v-for="tf in founded_templates"
              :key="tf.pk"
              class="founded-template"
              @click="do_select_researches(tf.researches)"
            >
              {{ tf.title }}
            </div>
          </div>
          <input
            id="template-search"
            v-model="search_template"
            type="text"
            placeholder="Поиск шаблона"
            class="form-control"
            style="width: calc(100% - 35px); max-width: 300px"
          >
          <button
            v-tippy="{ placement: 'top', arrow: true }"
            class="btn btn-blue-nb bottom-inner-btn"
            style="width: 35px"
            title="Очистить поиск"
            @click="clear_search_template"
          >
            <span>&times;</span>
          </button>
        </div>
        <input
          id="fndsrc"
          ref="fndsrc"
          v-model="search"
          v-tippy="{
            html: '#founded-n',
            trigger: 'mouseenter focus input',
            reactive: true,
            arrow: true,
            animation: 'fade',
            duration: 0,
          }"
          type="text"
          placeholder="Поиск назначения (Enter для быстрого выбора и очистки)"
          class="form-control"
          style="max-width: 300px"
          @keyup.enter="founded_select(true)"
          @show="check_found_tip"
          @shown="check_found_tip"
          @keyup.alt.37="k('left')"
          @keyup.alt.38="k('up')"
          @keyup.alt.39="k('right')"
          @keyup.alt.40="k('down')"
        >
        <button
          v-tippy="{ placement: 'top', arrow: true }"
          class="btn btn-blue-nb bottom-inner-btn"
          title="Быстрый выбор найденного"
          @click="founded_select"
        >
          <span class="fa fa-circle" />
        </button>
        <button
          v-tippy="{ placement: 'top', arrow: true }"
          class="btn btn-blue-nb bottom-inner-btn"
          title="Очистить поиск"
          @click="clear_search"
        >
          <span>&times;</span>
        </button>
      </div>
    </div>
    <div
      v-else-if="just_search"
      class="bottom-picker"
      style="white-space: nowrap"
    >
      <input
        ref="fndsrc"
        v-model="search"
        v-tippy="{
          html: '#founded-n',
          trigger: 'mouseenter focus input',
          reactive: true,
          arrow: true,
          animation: 'fade',
          duration: 0,
        }"
        type="text"
        placeholder="Поиск назначения (Enter для быстрого выбора и очистки)"
        class="form-control"
        style="width: calc(100% - 68px); max-width: 100%"
        @keyup.enter="founded_select(true)"
        @show="check_found_tip"
        @shown="check_found_tip"
        @keyup.alt.37="k('left')"
        @keyup.alt.38="k('up')"
        @keyup.alt.39="k('right')"
        @keyup.alt.40="k('down')"
      >
      <button
        v-tippy="{ placement: 'top', arrow: true }"
        class="btn btn-blue-nb bottom-inner-btn"
        title="Быстрый выбор найденного"
        @click="founded_select"
      >
        <span class="fa fa-circle" />
      </button>
      <button
        v-tippy="{ placement: 'top', arrow: true }"
        class="btn btn-blue-nb bottom-inner-btn"
        title="Очистить поиск"
        @click="clear_search"
      >
        <span>&times;</span>
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { debounce } from 'lodash/function';

import * as actions from '@/store/action-types';
import CategoryPick from '@/ui-cards/CategoryPick.vue';

import ResearchPick from './ResearchPick.vue';

export default {
  name: 'ResearchesPicker',
  components: { CategoryPick, ResearchPick },
  props: {
    value: {},
    autoselect: {
      default: 'directions',
    },
    hidetemplates: {
      default: false,
      type: Boolean,
    },
    oneselect: {
      default: false,
      type: Boolean,
    },
    readonly: {
      default: false,
      type: Boolean,
      required: false,
    },
    just_search: {
      default: false,
      type: Boolean,
      required: false,
    },
    filter_types: {
      default() {
        return [];
      },
      type: Array,
      required: false,
    },
    filter_sub_types: {
      default() {
        return [];
      },
      type: Array,
      required: false,
    },
    filter_researches: {
      default() {
        return [];
      },
      type: Array,
      required: false,
    },
    kk: {
      type: String,
      default: '',
    },
    typesOnly: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    return {
      type: '-1',
      dep: -1,
      template: -1,
      selectedSubcategory: -1,
      checked_researches: [],
      search: '',
      search_template: '',
      founded_templates: [],
    };
  },
  computed: {
    hide_grouped_researches() {
      return Boolean(this.autoselect !== 'directions' || this.oneselect || this.hidetemplates);
    },
    l2_only_doc_call() {
      return this.$store.getters.modules.l2_only_doc_call;
    },
    l2_without_lab_and_paraclinic() {
      return this.$store.getters.modules.l2_without_lab_and_paraclinic;
    },
    l2_research_col() {
      return this.$store.getters.modules.l2_research_select_col;
    },
    l2_all_service() {
      return this.$store.getters.modules.l2_all_service;
    },
    types() {
      let result = this.$store.getters.allTypes.filter(
        (row) => row.pk !== '0'
          && row.pk !== '1'
          && !this.filter_types.includes(parseInt(row.pk, 10))
          && (this.typesOnly.length === 0 || this.typesOnly.includes(parseInt(row.pk, 10)))
          && (!this.l2_only_doc_call || row.pk === '4' || row.pk === '14')
          && (!this.$asVI() || row.pk !== '2')
          && row.pk !== '13'
          && (!this.l2_without_lab_and_paraclinic || (row.pk !== '2' && row.pk !== '3')),
      );

      if (result.length > 1) {
        result = [
          ...result,
          {
            pk: '-109999',
            title: 'Частый выбор',
          },
        ];
      }

      if (this.typesOnly && this.typesOnly.length > 0) {
        result = this.typesOnly.map((t) => result.find((r) => Number(r.pk) === Number(t))).filter(Boolean);
      } else {
        result = result.filter((r) => Number(r.pk) !== 14);
      }

      return result;
    },
    selected_type() {
      for (const t of this.types) {
        if (t.pk === this.type) {
          return t;
        }
      }
      return { title: 'Не выбран тип', pk: '-1' };
    },
    selectedSubcategoryObj() {
      return this.subcategories.find((c) => c.pk === this.selectedSubcategory) || {};
    },
    subcategory_base() {
      if (this.dep === 10001) {
        return 8;
      }
      return null;
    },
    work_as_subcategory() {
      return this.subcategory_base !== null;
    },
    subcategories() {
      if (!this.work_as_subcategory) {
        return [];
      }
      let sc = this.$store.getters.ex_dep[this.subcategory_base] || [];
      sc = sc.map((c) => {
        const researches = this.researches_sub_categories(c.pk);
        const selected = researches.filter(({ pk }) => this.checked_researches.includes(pk)).length;
        return { ...c, researches, selected };
      });
      return sc.filter((c) => c.researches.length > 0);
    },
    selected_type_i() {
      let i = 0;
      for (const t of this.types) {
        if (t.pk === this.type) {
          return i;
        }
        i++;
      }
      return i;
    },
    t() {
      return parseInt(this.type || 0, 10);
    },
    rev_t() {
      return this.is_doc_ref ? 2 - this.t : this.t;
    },
    is_doc_ref() {
      return parseInt(this.type || 0, 10) > 3;
    },
    departments_of_type() {
      if (this.is_doc_ref) {
        if (this.filter_sub_types.length === 0) {
          return this.$store.getters.ex_dep[this.type];
        }
        return this.$store.getters.ex_dep[this.type].filter((t) => this.filter_sub_types.includes(t.pk));
      }
      const r = [];
      for (const row of this.$store.getters.allDepartments) {
        if (row.type === this.type && (this.filter_sub_types.length === 0 || this.filter_sub_types.includes(row.pk))) {
          r.push(row);
        }
      }
      return r;
    },
    dep_i() {
      let i = 0;
      for (const row of this.departments_of_type) {
        if (row.pk === this.dep) {
          return i;
        }
        i++;
      }
      return i;
    },
    templates() {
      return this.$store.getters.templates;
    },
    researches_display() {
      return this.researches_dep_display().filter((research) => {
        const searchTerm = this.search.toLowerCase();
        const researchTitle = research.full_title?.toLowerCase();
        const researchShortTitle = research.title?.toLowerCase();
        const researchInternalCode = research.internal_code?.toLowerCase();
        return researchTitle.includes(searchTerm) || researchShortTitle.includes(searchTerm)
          || researchInternalCode.includes(searchTerm);
      });
    },
    founded_n() {
      let r = 'Не найдено';
      let n = 0;
      for (const row of this.researches_display) {
        if (this.highlight_search(row)) {
          n++;
        }
      }
      if (n > 0) {
        r = `Найдено ${n}`;
      }
      return r;
    },
  },
  watch: {
    l2_only_doc_call: {
      handler() {
        if (this.l2_only_doc_call) {
          this.select_type('4');
        }
      },
      immediate: true,
    },
    value(v) {
      if (v instanceof Array) {
        this.checked_researches = v;
      }
    },
    types() {
      this.checkType();
    },
    templates() {
      this.check_template();
    },
    checked_researches() {
      if (this.oneselect) {
        this.$emit('input', this.checked_researches.length === 0 ? -1 : this.checked_researches[0]);
        return;
      }
      this.$emit('input', this.checked_researches);
    },
    search() {
      this.check_found_tip();
    },
    search_template: debounce(function (nv) {
      this.do_search_template(nv);
    }, 80),
    subcategories() {
      if (this.subcategories.length === 0) {
        this.selectedSubcategory = -1;
      }
    },
  },
  created() {
    this.$store.watch(
      (state) => state.templates,
      () => {
        this.check_template();
      },
      { immediate: true },
    );

    this.$store.watch(
      (state) => state.allTypes,
      () => {
        this.checkType();
      },
      { immediate: true },
    );

    this.$store.watch(
      (state) => state.templates,
      () => {
        this.check_template();
      },
      { immediate: true },
    );
  },
  async mounted() {
    this.$root.$on(`researches-picker:deselect${this.kk}`, this.deselect_research_ignore);
    this.$root.$on(`researches-picker:deselect_department${this.kk}`, this.deselect_department);
    this.$root.$on(`researches-picker:deselect_all${this.kk}`, this.clear);
    this.$root.$on(`researches-picker:add_research${this.kk}`, this.select_research_ignore);

    if (!this.$store.getters.okDep || Object.keys(this.$store.getters.researches).length === 0) {
      await this.$store.dispatch(actions.INC_LOADING);

      await Promise.all([this.$store.dispatch(actions.GET_RESEARCHES), this.$store.dispatch(actions.GET_TEMPLATES)]);

      await this.$store.dispatch(actions.DEC_LOADING);
    }

    this.checkType();
    this.check_template();

    if (this.value instanceof Array) {
      this.checked_researches = this.value;
    }
  },
  methods: {
    researches_sub_categories(scId) {
      const r = [];
      for (const row of this.$store.getters.researches[this.rev_t] || []) {
        if (row.site_type_raw === scId && row.site_type === this.dep) {
          r.push(row);
        }
      }
      return r.filter((x) => !this.filter_researches.includes(x.pk) && (!this.hide_grouped_researches || !x.auto_deselect));
    },
    researches_dep_display(dep = this.dep) {
      let r = [];
      if (this.rev_t === -2 || dep === -13) {
        for (const d of Object.keys(this.$store.getters.researches)) {
          for (const row of this.$store.getters.researches[d] || []) {
            if ((row.doc_refferal || row.is_application) && row.site_type === dep) {
              r.push(row);
            }
          }
        }
      } else if (this.rev_t < -2) {
        for (const row of this.$store.getters.researches[this.rev_t] || []) {
          if (row.site_type === dep || (dep === -1 && !row.site_type)) {
            r.push(row);
          }
        }
      } else if (this.dep in this.$store.getters.researches) {
        r = this.$store.getters.researches[dep];
      }
      return r.filter((x) => !this.filter_researches.includes(x.pk) && (!this.hide_grouped_researches || !x.auto_deselect));
    },
    k(t) {
      let n = 0;
      switch (t) {
        case 'left':
          n = this.dep_i - 1;
          if (n < 0) {
            n = this.departments_of_type.length - 1;
          }
          this.select_dep(this.departments_of_type[n].pk);
          break;
        case 'right':
          n = this.dep_i + 1;
          if (n > this.departments_of_type.length - 1) {
            n = 0;
          }
          this.select_dep(this.departments_of_type[n].pk);
          break;
        case 'up':
          n = this.selected_type_i + 1;
          if (n > this.types.length - 1) {
            n = 0;
          }
          this.select_type(this.types[n].pk);
          break;
        case 'down':
          n = this.selected_type_i - 1;
          if (n < 0) {
            n = this.types.length - 1;
          }
          this.select_type(this.types[n].pk);
          break;
        default:
          break;
      }
    },
    check_found_tip() {
      const el = this.$refs.fndsrc;
      // eslint-disable-next-line no-underscore-dangle
      if (this.search === '' && '_tippy' in el && el._tippy.state.visible) {
        // eslint-disable-next-line no-underscore-dangle
        el._tippy.hide();
      }
    },
    select_type(pk) {
      this.type = pk;
      this.checkType();
    },
    select_dep(pk) {
      this.dep = pk;
      window.$(this.$refs.fndsrc).focus();
    },
    checkType() {
      if (this.type === '-109999') {
        this.$store.dispatch(actions.GET_LAST_USED_RESEARCHES);
      }
      if (this.types.length > 0 && !this.types.map((t) => Number(t.pk)).includes(Number(this.type))) {
        this.type = JSON.parse(JSON.stringify(this.types[0].pk));
      }
      for (const row of this.departments_of_type) {
        if (this.dep === row.pk) {
          return;
        }
      }
      this.dep = this.departments_of_type.length > 0 ? this.departments_of_type[0].pk : -1;
    },
    check_template() {
      if (this.template === -1 && this.templates.length > 0) {
        this.template = JSON.parse(JSON.stringify(this.templates[0].pk));
      }
    },
    load_template(pk) {
      if (this.readonly) {
        return;
      }
      let lastDep = -1;
      let lastType = -1;
      for (const v of this.get_template(pk).values) {
        this.select_research_ignore(v);
        const d = this.research_data(v);
        lastDep = d.department_pk;
        lastType = d.type;
      }
      this.select_type(lastType);
      this.select_dep(lastDep);
    },
    get_template(pk) {
      for (const t of this.templates) {
        if (t.pk === pk) {
          return t;
        }
      }
      return {
        title: 'Не выбран шаблон',
        pk: '-1',
        for_current_user: false,
        for_users_department: false,
        values: [],
      };
    },
    select_research(pk) {
      if (this.readonly) {
        return;
      }
      if (this.oneselect) {
        this.checked_researches = [pk];
        return;
      }
      if (this.research_selected(pk)) {
        this.deselect_research_ignore(pk);
      } else {
        this.select_research_ignore(pk);
      }
    },
    select_research_ignore(pk) {
      if (this.readonly) {
        return;
      }
      if (!this.research_selected(pk)) {
        const research = this.research_data(pk);
        if (!research.auto_deselect) {
          this.checked_researches.push(pk);
        } else {
          this.$root.$emit('msg', 'ok', 'Применён шаблон');
        }
        if (this.autoselect === 'directions' && research.autoadd) {
          for (const autoaddPk of research.autoadd) {
            this.select_research_ignore(autoaddPk);
          }
        }
      }
    },
    deselect_research_ignore(pk) {
      if (this.readonly) {
        return;
      }
      if (this.research_selected(pk)) {
        this.checked_researches = this.checked_researches.filter((item) => item !== pk);
        const research = this.research_data(pk);
        if (this.autoselect === 'directions') {
          for (const addtoPk of research.addto || []) {
            this.deselect_research_ignore(addtoPk);
          }
        }
      }
    },
    deselect_department(pk) {
      if (this.readonly) {
        return;
      }
      for (const rpk of this.researches_selected_in_department(pk, true)) {
        this.deselect_research_ignore(rpk);
      }
    },
    clear() {
      this.checked_researches = [];
      if (this.type === '-109999') {
        this.$store.dispatch(actions.GET_LAST_USED_RESEARCHES);
      }
    },
    research_selected(pk) {
      return this.checked_researches.indexOf(pk) !== -1;
    },
    clear_search() {
      this.search = '';
      window.$(this.$refs.fndsrc).focus();
    },
    founded_select(clearOrig = false) {
      const clear = clearOrig || false;
      for (const row of this.researches_display) {
        if (this.highlight_search(row)) {
          this.select_research_ignore(row.pk);
        }
      }
      if (clear) {
        this.clear_search();
      } else {
        window.$(this.$refs.fndsrc).focus();
      }
    },
    highlight_search(row) {
      const t = row.title.toLowerCase().trim();
      const ft = row.full_title.toLowerCase().trim();
      const c = row.code.toLowerCase().trim().replace('а', 'a').replace('в', 'b');
      const s = this.search.toLowerCase().trim();
      return s !== '' && (t.includes(s) || ft.includes(s) || c.startsWith(s.replace('а', 'a').replace('в', 'b')));
    },
    research_data(pk) {
      if (pk in this.$store.getters.researches_obj) {
        return this.$store.getters.researches_obj[pk];
      }
      return {};
    },
    researches_selected_in_department(pk, prim) {
      const r = [];
      if (prim) {
        for (const rpk of this.checked_researches) {
          const res = this.research_data(rpk);
          if (res.department_pk === pk || (pk === -2 && res.doc_refferal)) {
            r.push(rpk);
          }
        }
      } else {
        for (const rpk of this.checked_researches) {
          const res = this.research_data(rpk);
          if (this.rev_t < -2 && res.department_pk === this.rev_t && ((!res.site_type && !pk) || res.site_type === pk)) {
            r.push(rpk);
          } else if (
            this.rev_t >= -2
            && ((res.department_pk === pk && (!res.doc_refferal || !this.is_doc_ref || pk === -2))
              || (this.is_doc_ref && res.site_type === pk && res.doc_refferal)
              || (!res.site_type && res.doc_refferal && pk === -2))
          ) {
            r.push(rpk);
          }
        }
      }
      return r;
    },
    researches_selected_in_type(pk) {
      let l = 0;
      for (const rpk of this.checked_researches) {
        const res = this.research_data(rpk);
        if (
          (res.type === pk && !res.doc_refferal && !res.treatment && !res.stom)
          || (pk === '4' && res.doc_refferal)
          || (pk === '5' && res.treatment)
          || (pk === '6' && res.stom)
          || (pk === '7' && res.is_hospital)
        ) {
          l++;
        }
      }
      return l > 0 ? ` (${l})` : '';
    },
    researches_selected_in_type_list(pk) {
      const l = [];
      for (const rpk of this.checked_researches) {
        const res = this.research_data(rpk);
        if (
          (res.type === pk && !res.doc_refferal && !res.treatment && !res.stom)
          || (pk === '4' && res.doc_refferal)
          || (pk === '5' && res.treatment)
          || (pk === '6' && res.stom)
          || (pk === '7' && res.is_hospital)
        ) {
          l.push(res);
        }
      }
      return l;
    },
    do_search_template(nv) {
      this.founded_templates = [];
      if (nv === '') return;
      fetch(`/api/search-template?q=${encodeURIComponent(nv)}`)
        .then((q) => q.json())
        .then((data) => {
          this.founded_templates = (data.result || []).slice().reverse();
        });
    },
    do_select_researches(pks) {
      if (pks.length === 0) {
        return;
      }

      for (const pk of pks) {
        this.select_research_ignore(pk);
      }

      const d = this.research_data(pks[pks.length - 1]);
      this.select_type(d.type);
      if (d.type !== '4') {
        this.select_dep(d.department_pk);
      }
      this.clear_search_template();
    },
    clear_search_template() {
      this.search_template = '';
    },
  },
};
</script>

<style scoped lang="scss">
.top-picker,
.bottom-picker {
  height: 34px;
  background-color: #aab2bd;
  position: absolute;
  left: 0;
  right: 0;
}

.top-picker {
  top: 0;
}

.top-inner,
.content-picker,
.content-none {
  display: flex;
  flex-wrap: wrap;
  justify-content: stretch;
  align-content: center;
  align-items: stretch;
  overflow-y: auto;
}

.content-picker {
  align-content: flex-start;
}

.content-none {
  align-items: center;
  align-content: center;
  justify-content: center;
}

.top-inner {
  position: absolute;
  left: 139px;
  top: 0;
  right: 0;
  height: 34px;
  align-content: stretch;
  overflow: hidden;
}

.top-inner-right {
  right: 120px;
}

.top-inner-select,
.research-select {
  align-self: stretch;
  display: flex;
  align-items: center;
  padding: 1px 2px 1px;
  color: #000;
  background-color: #fff;
  text-decoration: none;
  transition: 0.15s linear all;
  cursor: pointer;
  flex: 1;
  margin: 0;
  font-size: 12px;
  min-width: 0;
}

.top-inner-select {
  background-color: #aab2bd;
  color: #fff;
}

.category-title {
  flex: 0 1 100%;
  width: 100%;
  height: 34px;
  border: 1px solid #6c7a89 !important;
  margin-bottom: 5px;
  padding: 8px;
  text-align: left;
  font-weight: bold;
}

.research-select {
  flex: 0 1 auto;
  width: 25%;
  height: 34px;
  border: 1px solid #6c7a89 !important;
  cursor: pointer;
  text-align: left;
  outline: transparent;
}

.top-inner-select.active,
.research-select.active {
  background: #049372 !important;
  color: #fff;
}

.top-inner-select > span {
  display: block;
  text-overflow: ellipsis;
  overflow: hidden;
  word-break: keep-all;
  max-height: 2.2em;
  line-height: 1.1em;
}

.top-inner-select:hover {
  background-color: #434a54;
}

.research-select:hover {
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.8) !important;
}

.highlight_search {
  background: #07f6bf;
  color: #000;
}

.content-picker,
.content-none {
  position: absolute;
  top: 34px;

  &:not(.hidetemplates) {
    bottom: 34px;
  }

  &.hidetemplates {
    bottom: 0;
  }

  left: 0;
  right: 0;
  overflow-y: auto;
}

.bottom-picker {
  bottom: 0;
  display: flex;
  justify-content: space-between;
  font-size: 11px;

  input {
    max-width: 350px;
    width: 100%;
    border-left: none;
    border-bottom: none;
    border-right: none;
    border-radius: 0;
  }
}

.bottom-inner-btn {
  width: auto;
  text-align: center;
  border-radius: 0;
}

#templates-tip {
  position: absolute;
  bottom: 34px;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 5px 5px 0 0;
  overflow: hidden;
  box-shadow: 0 -2px 2px rgba(0, 0, 0, 0.4);
}

.founded-template {
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;

  &:hover {
    background: #049372;
    color: #fff;
  }
}

.bt1 {
  width: 139px;
  text-align: left !important;
  border-radius: 0;
  padding: 7px 5px;
  font-size: 13px;
}
.all-dep {
  width: 30px;
  flex: none;
}
.research-select-col {
  &--1 {
    width: 100%;
  }
  &--2 {
    width: 50%;
  }
  &--3 {
    width: 33.3%;
  }
}
.depart-other {
  float: right;
  width: 120px;
  text-align: right !important;
  box-shadow: none !important;
  border-radius: 0;
}
.depart-other-btn {
  float: left;
  font-size: 12px;
  height: 34px;
}
.depart-other-dropdown {
  position: relative;
  float: right;
  text-align: right;
  max-height: 250px;
  overflow-y: auto;
}
</style>
