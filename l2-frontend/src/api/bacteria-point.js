import {generator} from './http-common'

export default generator({
  loadGroups: {
    url: 'bacteria/loadculture',
    onReject: {ok: false},
  },
  saveElement: {
    url: 'bacteria/saveculture',
  },
  saveGroup: {
    url: 'bacteria/savegroup',
  },
  updateGroup: {
    url: 'bacteria/updategroup',
  },
  addNewGroup: {
    url: 'bacteria/addnewgroup',
  },
  loadantibioticset: {
    url: 'bacteria/loadantibioticset',
  },
  loadCultures: {
    url: 'bacteria/loadculture',
  },
  loadSetElements: {
    url: 'bacteria/loadsetelements',
  },

})