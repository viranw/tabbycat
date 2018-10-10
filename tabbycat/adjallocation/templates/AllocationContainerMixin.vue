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
    handleSocketReceive (socketLabel, payload) {
      console.log('handleSocketReceive', payload)
      // Receive debate objects with a list of attributes from the websocket

      let removedAdjudicators = []

      // Loop over keys received and set their reactive properties on the local objects
      Object.entries(payload).forEach(([debateOrPanelId, debateOrPanelChanges]) => {
        Object.entries(debateOrPanelChanges).forEach(([attribute, value]) => {
          let debate = this.debatesById[debateOrPanelId]
          if (attribute === 'adjudicators') {
            debate.debateAdjudicators.forEach((debateAdjudicator) => {
              removedAdjudicators.push(debateAdjudicator.adjudicator)
            })
            debate.debateAdjudicators = value
            // See if the new debate adjudicators include any of the old adjudicators
            debate.debateAdjudicators.forEach((newDebateAdjudicator) => {
              // Remove them from the removed list if so
              let index
              index = removedAdjudicators.findIndex((removedAdj) => {
                return removedAdj.id === newDebateAdjudicator.adjudicator.id
              })
              if (index !== -1) {
                removedAdjudicators.splice(index, 1)
              }
              // Remove them from the unallocated list
              index = this.unallocatedItems.findIndex((unallocatedAdj) => {
                return unallocatedAdj.id === newDebateAdjudicator.adjudicator.id
              })
              if (index !== -1) {
                this.unallocatedItems.splice(index, 1)
              }
            })
          } else {
            debate[attribute] = value
          }
          debate.locked = false
        })
      })
      // Now need to loop through all the returned debates
      removedAdjudicators.forEach((removedAdjudicator) => {
        this.unallocatedItems.push(removedAdjudicator)
      })
    },
    updateUnallocatedSorting (sortType) {
      this.unallocatedSortOrder = sortType
    },
  },
}
</script>
