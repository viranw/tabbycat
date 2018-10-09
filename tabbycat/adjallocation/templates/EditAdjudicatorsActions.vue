<template>

  <allocation-actions :round-info="roundInfo" :sharding="sharding.enabled"
                      :percentiles="percentileThresholds">

    <template slot="extra-actions">
      <a :class="['btn text-white', sharding ? 'disabled btn-secondary' : 'btn-success']"
         data-toggle="modal" data-target="#confirmAutoAllocationModal">
        Auto-Allocate
      </a>
      <a :class="['btn text-white', sharding ? 'btn-primary' : 'btn-success']"
         data-toggle="modal" data-target="#confirmShardingModal">
        <span data-toggle="tooltip" data-placement="bottom"
         title="Limit this view to a shard (specific subsection) of this draw">
          <i data-feather="server"></i>
        </span>
      </a>
    </template>

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
      this.saveMove(payload.adjudicator, payload.debate)
    },
  },
}

</script>
