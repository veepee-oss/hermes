<template>
    <div>
        <div class="h-100 bg-plum-plate bg-animation">
            <div class="d-flex h-100 justify-content-center align-items-center">
                <b-col md="8" class="mx-auto app-login-box">

                    <div class="modal-dialog w-100 mx-auto">
                        <div class="modal-content">
                            <div class="modal-body">
                                <div class="h5 modal-title text-center">
                                    <h4 class="mt-2">
                                        <div><img src="/icons/logo.png" width="30" style="margin-right:10px">Hermes</div>
                                    </h4>
                                </div>
                                <b-form-group>
                                    <b-form-input v-model="usernameText"
                                                  type="email"
                                                  required
                                                  placeholder="Enter email...">
                                    </b-form-input>
                                </b-form-group>
                                <b-form-group>
                                              
                                    <b-form-input  v-model="passwordText"
                                                  type="password"
                                                  required
                                                  placeholder="Enter password...">
                                    </b-form-input>
                                </b-form-group>
                            </div>
                            <div class="modal-footer clearfix">
                                <div v-if="errorPresent" class="float-left" style="color: red; margin-right: 10px">
                                    Error: {{errorMsg}}
                                </div>
                                <div class="float-right">
                                    <b-button v-bind:disabled="isLoginDisabled" variant="primary" v-on:click="logMe" size="lg">Login</b-button>
                                </div>
                            </div>
                        </div>
                    </div>
                </b-col>
            </div>
        </div>
    </div>
</template>
<script>

export default {
    name: 'login',
    data() {
        return {            
            usernameText: '',
            passwordText: '',

            isLoginDisabled: false,
            errorPresent: false,
            errorMsg: ''
        }
    },
    mounted: function(){
        let obj_t = this;
        document.addEventListener('keydown', function(e){
            if (e.key == 'Enter') {
                obj_t.logMe();
            }
        });
    },
    methods: {
        logMe: function(){
            this.errorPresent = false;
            this.isLoginDisabled = true;

            this.$store.dispatch('retreiveToken',{
                email_username: this.usernameText,
                password: this.passwordText
            }).then(() => {
                this.isLoginDisabled = false;
                this.$router.push('/');
                
            }).catch(error => {
                this.isLoginDisabled = false;
                this.errorMsg = String(error);
                this.errorPresent = true;
            });
        }
    }
}
</script>
