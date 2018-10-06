<template>

  <allocation-actions :round-info="roundInfo" :sharding="sharding.enabled"
                      :percentiles="percentileThresholds">

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
