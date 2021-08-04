<template>
    <div class="d-flex">
        <div class="header-btn-lg pr-0">
            <div class="widget-content p-0">
                <div class="widget-content-wrapper">
                    <div v-if="loading_icon" class="widget-content-left mr-4">
                        <img src="loaders/69f69030-b057-4082-9cd0-b332bb07f548.gif" width="40" style="margin-right: 4px;"> 
                        <i>Refreshing ...</i>
                    </div>
                    <div class="widget-content-left">
                        <b-dropdown toggle-class="p-0 mr-2" menu-class="dropdown-menu-lg" variant="link" right>
                            <span slot="button-content">
                                <div class="icon-wrapper icon-wrapper-alt rounded-circle">
                                    <img width="35" class="rounded-circle" src="/avatars/avatar_male.png" alt="">
                                </div>
                            </span>
                            <button type="button" tabindex="0" class="dropdown-item">Settings</button>
                            <div tabindex="-1" class="dropdown-divider"></div>
                            <button type="button" tabindex="0" class="dropdown-item" v-on:click="logOut">Logout</button>
                        </b-dropdown>
                    </div>
                    <div class="widget-content-left ml-3">
                        <div class="widget-heading">Admin</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        components: {
            
        },
        data: () => ({
            loading_icon: false
        }),

        methods: {
            logOut: function(){
                this.$store.dispatch('destroyToken');
                this.$router.push('/login');
            },

            switchLoadingIcon: function(new_state){
                this.loading_icon = new_state;
            }
        }
    }


</script>
