<script>
// Shared methods between EditPanelsContainer and EditAdjudicatorsContainer

import _ from 'lodash'
import percentile from 'stats-percentile'

import DrawContainerMixin from '../../draw/templates/DrawContainerMixin.vue'
import AdjudicatorMovingMixin from '../../templates/ajax/AdjudicatorMovingMixin.vue'
import AutoImportanceLogicMixin from './AutoImportanceLogicMixin.vue'
import HighlightContainerMixin from '../../templates/allocations/HighlightContainerMixin.vue'

import AllocationIntroModal from '../../templates/allocations/AllocationIntroModal.vue'
import DebateImportance from '../../templates/allocations/DebateImportance.vue'
import DebatePanel from '../../templates/allocations/DebatePanel.vue'
import DraggableAdjudicator from '../../templates/draganddrops/DraggableAdjudicator.vue'
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'
import WebSocketMixin from '../../templates/ajax/WebSocketMixin.vue'

export default {
  mixins: [
    AjaxMixin, AdjudicatorMovingMixin, DrawContainerMixin,
    AutoImportanceLogicMixin, HighlightContainerMixin, WebSocketMixin,
  ],
  components: {
    AllocationIntroModal,
    DebateImportance,
    DebatePanel,
    DraggableAdjudicator,
  },
  props: { showIntroModal: Boolean },
  data: function () {
    return {
      unallocatedSortOrder: null,
    }
  },
  created: function () {
    // Watch for global conflict highlights
    this.$eventHub.$on('show-conflicts-for', this.setOrUnsetConflicts)
  },
  computed: {
    unallocatedAdjsByOrder: function () {
      if ((this.unallocatedSortOrder === null && this.roundInfo.roundIsPrelim === true) ||
           this.unallocatedSortOrder === 'score') {
        return _.reverse(_.sortBy(this.unallocatedItems, ['score']))
      }
      return _.sortBy(this.unallocatedItems, ['name'])
    },
    adjudicatorsById: function () {
      // Override DrawContainer() method to include unallocated
      return _.keyBy(this.adjudicators.concat(this.unallocatedItems), 'id')
    },
    percentileThresholds: function () {
      // For determining feedback rankings
      const allScores = _.map(this.adjudicatorsById, adj => parseFloat(adj.score)).sort()
      const thresholds = []
      const letterGrades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
      for (let i = 90; i > 10; i -= 10) {
        thresholds.push({
          grade: letterGrades[0], cutoff: percentile(allScores, i), percentile: i,
        })
        letterGrades.shift()
      }
      thresholds.push({ grade: 'F', cutoff: 0, percentile: 10 })
      return thresholds
    },
    adjPositions: function () {
      return this.roundInfo.adjudicatorPositions // Convenience
    },
  },
  methods: {
    handleSocketReceive (socketLabel, payload) {
      // Receive debate objects with a list of attributes from the websocket
      // Loop over keys received and set their reactive properties on the local objects
      Object.entries(payload).forEach(([debateOrPanelId, debateOrPanelChanges]) => {
        Object.entries(debateOrPanelChanges).forEach(([attribute, value]) => {
          this.debatesById[debateOrPanelId][attribute] = value
        })
      })
    },
    updateUnallocatedSorting (sortType) {
      this.unallocatedSortOrder = sortType
    },
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
