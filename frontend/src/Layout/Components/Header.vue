<template>
    <div class="app-header header-shadow" style="height: 40px !important">
        
        <div class="app-header__content">
            <div class="app-header-left">
                <router-link to="/" class="nav-link title_bar">
                    <img  src="/icons/logo.png" width="30" style="margin-right:10px"> Hermes
                </router-link>
                
                
            </div>
            <div class="app-header-right">
                <UserArea ref="HeaderUserAreaComponent"/>
            </div>
        </div>
    </div>
</template>

<script>
    import UserArea from './Header/HeaderUserArea';
    
    export default {
        name: "Header",
        components: {
            UserArea,
        },

        data() {
            return {
                isOpen: false,
                isOpenMobileMenu: false,
            }
        },
        props: {


        },
        methods: {
            toggleMobile(className) {
                const el = document.body;
                this.isOpen = !this.isOpen;

                if (this.isOpen) {
                    el.classList.add(className);
                } else {
                    el.classList.remove(className);
                }
            },

            toggleMobile2(className) {
                const el = document.body;
                this.isOpenMobileMenu = !this.isOpenMobileMenu;

                if (this.isOpenMobileMenu) {
                    el.classList.add(className);
                } else {
                    el.classList.remove(className);
                }
            },


            switchHeaderLoadingIcon: function(new_state){
                this.$refs['HeaderUserAreaComponent'].switchLoadingIcon(new_state);
            }
        }
    };
</script>
