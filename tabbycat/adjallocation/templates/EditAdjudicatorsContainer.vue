<template>
  <div class="draw-container allocation-container">

    <edit-adjudicators-actions :round-info="roundInfo" :sharding="sharding.enabled"
                               :percentiles="percentileThresholds"></edit-adjudicators-actions>

    <div class="row">
      <div class="mt-3 col allocation-messages" id="messages-container"></div>
    </div>

    <div class="mb-3">
      <draw-header :round-info="roundInfo" @resort="updateSorting"
                   :sort-key="sortKey" :sort-order="sortOrder">

        <div slot="himportance" class="thead flex-cell flex-6 vue-sortable"
             @click="updateSorting('importance')" data-toggle="tooltip"
             title="The debate's priority. Higher priorities will be allocated
              better adjudicators during auto-allocation." >
          <div class="d-flex align-items-end">
            <span class="tooltip-trigger">Priority</span>
            <div :class="sortClasses('importance')">
              <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
            </div>
          </div>
        </div>

        <template slot="hvenue">
          <span></span> <!-- Hide Venues -->
        </template>

        <template slot="hpanel">
          <div :class="[
              'thead flex-cell text-center',
              'flex-' + (adjPositions.length > 2 ? 10 : adjPositions.length > 1 ? 8 : 12)]">
            <div class="d-flex align-items-end">
              <span>Chair</span>
            </div>
          </div>
          <div v-if="adjPositions.indexOf('P') !== -1"
               :class="['thead flex-cell text-center',
                        'flex-' + (adjPositions.length > 2 ? 17: 16)]">
            <div class="d-flex align-items-end">
              <span>Panellists</span>
            </div>
          </div>
          <div v-if="adjPositions.indexOf('T') !== -1"
               :class="['thead flex-cell text-center',
                        'flex-' + (adjPositions.length > 2 ? 10: 16)]">
            <div class="d-flex align-items-end">
              <span>Trainees</span>
            </div>
          </div>
        </template>

      </draw-header>

      <debate v-for="debate in dataOrderedByKey"
              :debate="debate"
              :key="debate.id" :round-info="roundInfo">

        <div class="draw-cell flex-6" slot="simportance">
          <debate-importance :id="debate.id" :importance="debate.importance"></debate-importance>
        </div>

        <template slot="svenue">
          <span></span> <!-- Hide Venues -->
        </template>

        <template slot="spanel">
          <debate-panel :panel-adjudicators="debate.debateAdjudicators" :debate-id="debate.id"
                        :panel-teams="debate.debateTeams"
                        :percentiles="percentileThresholds"
                        :locked="debate.locked"
                        :round-info="roundInfo"
                        :adj-positions="adjPositions"></debate-panel>
        </template>

      </debate>
    </div>

    <unallocated-items-container v-if="!sharding.enabled">
      <div v-for="unallocatedAdj in unallocatedAdjsByOrder">
        <draggable-adjudicator :adjudicator="unallocatedAdj"
                               :percentiles="percentileThresholds"
                               :locked="unallocatedAdj.locked"></draggable-adjudicator>
      </div>
      <div class="sort-handler align-items-center">
        <div v-if="unallocatedAdjsByOrder.length > 5"
             class="btn-group btn-group-toggle mt-2 mb-1 ml-2" data-toggle="buttons">
          <label class="btn btn-sm btn-secondary active"
                 @click="updateUnallocatedSorting('score')">
            <input type="radio" checked>By Score
          </label>
          <label class="btn btn-sm btn-secondary"
                 @click="updateUnallocatedSorting('name')">
            <input type="radio">By Name
          </label>
        </div>
      </div>
    </unallocated-items-container>

    <slide-over :subject="slideOverSubject"></slide-over>
    <allocation-intro-modal :show-intro-modal="showIntroModal"
                            :round-info="roundInfo"></allocation-intro-modal>

  </div>
</template>

<script>
import AllocationContainerMixin from './AllocationContainerMixin.vue'
import EditAdjudicatorsActions from './EditAdjudicatorsActions.vue'

export default {
  mixins: [AllocationContainerMixin],
  components: { EditAdjudicatorsActions },
  data: function () {
    return {
      sockets: ['debates'],
    }
  },
}
</script>
