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
import AllocationActions from '../../templates/allocations/AllocationActions.vue'

export default {
  props: {
    roundInfo: Object, percentiles: Array, sharding: Boolean,
  },
  components: {
    AllocationActions,
  },
}

</script>
