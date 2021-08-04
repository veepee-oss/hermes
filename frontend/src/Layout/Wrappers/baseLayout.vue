<template>
    <div class="app-container app-theme-white">
        <div class="row" style="height: 50px">
            <div class="col">
                <Header ref="HeaderComponent" />
            </div>
        </div>
        <div class="row">
            <div class="col" style="margin-left: 20px; margin-right: 20px;">
                <slot></slot>
            </div>
        </div>
    </div>
</template>

<script>
    import Header from "../Components/Header";

    export default {
        name: 'app',
        components: {
            Header
        },
        methods: {
            switchHeaderLoadingIcon: function(new_state){
                this.$refs['HeaderComponent'].switchHeaderLoadingIcon(new_state);
            }
        },
    }
</script>

<style>
.app-sidebar{
    width: 140px !important;
}

.app-main__outer{
    padding: 60px 0 0 140px !important;
}

.app-header__content{
    padding-left: 0px !important;
}

.app-main__inner{
    padding: 10px !important;
}
</style>
