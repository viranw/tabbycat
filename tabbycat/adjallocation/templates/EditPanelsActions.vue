<template>

  <allocation-actions :round-info="roundInfo" :sharding="sharding.enabled"
                      :percentiles="percentileThresholds">

  </allocation-actions>

</template>

<script>
import _ from 'lodash'

import AllocationActions from '../../templates/allocations/AllocationActions.vue'

export default {
  props: {
    roundInfo: Object, percentiles: Array, sharding: Boolean,
  },
  components: {
    AllocationActions,
  },
  methods: {
    moveToDebate (payload, assignedId, assignedPosition) {
      if (payload.debate === assignedId) {
        // Check that it isn't an in-panel move
        const thisDebate = this.debatesById[payload.debate]
        const debateAdjs = thisDebate.debateAdjudicators
        const fromPanellist = _.find(debateAdjs, da => da.adjudicator.id === payload.adjudicator)
        if (assignedPosition === fromPanellist.position) {
          return // Moving to same debate/position; do nothing
        }
      }
      this.saveMove(payload.adjudicator, payload.debate, assignedId, assignedPosition)
    },
    moveToUnused (payload) {
      if (_.isUndefined(payload.debate)) {
        return // Moving to unused from unused; do nothing
      }
      let debate = payload.debate
      let sentPayload = { debatesOrPanels: {} }
      sentPayload.debatesOrPanels[debate.id] = { 'adjudicators': debate.panelAdjudicators }
      console.log('sentPayload', sentPayload)
      this.sendToSocket(this.sockets[0], sentPayload)
    },
  },
}
</script>
