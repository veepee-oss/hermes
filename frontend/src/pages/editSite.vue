<template>
    <div v-if="!loading_main" class="lander_main_component">
        <div class="mb-3 card">
            <div class="no-gutters row">
                <div class="col-sm-6 col-md-12 col-xl-12">
                    <div class="row" style="padding: 15px;">
                        <div class="col-12">
                            <div class="row">
                                <div class="col-12">
                                    Regex: <b>{{unhexed_regex}}</b>
                                </div>
                            </div>
                            <div class="row" style="margin-top: 8px;">
                                <div class="col-12">
                                    Site HEX code: <b>{{$route.query.site_hex}}</b>
                                </div>
                            </div>
                        </div>
                    </div>
                    <b-tabs pills card>
                        <b-tab title="Blacklist detection" active>
                            <b-card-text>
                                <div class="row">
                                    <div class="col-8">
                                        The JS interpreter running this code is <b>Node</b>. It supports <b>Promises and Async functions</b>. Check doc for Syntax.
                                    </div>
                                    <div class="col-4" style="text-align: right">
                                        <button v-on:click="gen_example_bl_detect_code()" class="mt-1 btn btn-info btn-sm">Generate example code</button>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12">
                                        You may want to click on <b>Generate example code</b> to have a simple example with inputs explication
                                    </div>
                                </div>
                                <div class="row" style="min-height: 400px; margin-top: 20px;">
                                    <div class="col-12">
                                        <prism-editor v-on:submit.prevent class="editor_config_headers_function" v-model="code_site_blacklist_detect" :highlight="highlighter_js" line-numbers></prism-editor>
                                    </div>
                                </div>
                            </b-card-text>
                        </b-tab>
                        <template #tabs-end>
                            <b-nav-item href="#" @click="save_site" align="right">Save site</b-nav-item>
                        </template>
                        
                    </b-tabs>
                </div>
            </div>
        </div>
        
        
    </div>
    <div v-else style="display: grid; place-items: center; ">
        <div class="h-100" style="80vh !important">
            <div class="d-flex h-100 justify-content-center align-items-center">
                <div class="row">
                    <div class="col">
                        <div class="row">
                            <div class="col"><img src="loaders/69f69030-b057-4082-9cd0-b332bb07f548.gif" width="220"></div>
                        </div>
                        <div class="row" style="margin-top: 20px;">
                            <div class="col"><center style="font-size: 30px;"><b>Loading ...</b></center></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    

</template>

<script>

// import Prism Editor
import { PrismEditor } from 'vue-prism-editor';
import 'vue-prism-editor/dist/prismeditor.min.css'; // import the styles somewhere

// import highlighting library (you can use any library you want just return html string)
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-json';
import 'prismjs/themes/prism-twilight.css'; // import syntax highlighting styles


export default {
    name: 'editConf',
    components: {
        PrismEditor
    },
    data: () => ({
        loading_main: false,
        unhexed_regex: '',
        code_site_blacklist_detect: ''
    }),
    mounted: function(){
        this.fetch_def(this.$route.query.site_hex);
    },

    methods: {
        highlighter_js(code) {
            return highlight(code, languages.js); // languages.<insert language> to return html with markup
        },

        gen_example_bl_detect_code: function(){
            this.code_site_blacklist_detect = `// --------------------------------------------------------- 
// Do not change these lines: used to pass input data
const fs = require('fs');
const input_data = JSON.parse(fs.readFileSync(process.argv[2]));
/* --------------------------------------------------------- 
   ----- input_data : will have this structure (used with advanced proxy config)

{
   'reply':{
      'code': 200,
      'header': 'HTTP/1.1 200 OK\\r\\nContent-Type: text/html;charset=UTF-8\\r\\nContent-Encoding: gzip\\r\\nConnection: close',
      'data': '<!doctype html>\\n<html lang="fr">\\n<head>\\n Some HTML code... </html>'
   },
   'proxy':{
      'host': ('192.168.0.1', 8080)
      'auth': null,
      'log':{
        'stdout': '{"port":8080,"host":"192.168.0.1","password":null,"user":null}',
        'stderr': '',
        'execerr': '',
        'data_carried': 'Some proxy id to renew for eg',
        'note': 'no authentication needed'
      }
   }
}
   --------------------------------------------------------- */
// ---------------------------------------------------------
// You should always return 0 (not blacklisted) or 1 (blacklisted)

if (String(input_data['reply']['data']).includes("blacklisted")){
  console.log(1);
}else{
  console.log(0);
}`;
        },
    
        fetch_def(site_hex){
            let this_obj = this;
            this.$store.axios_obj.get('/sites/get/' + String(site_hex),{
                headers: {
                    Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                }
            })
            .then(response =>{
                if (response === null){
                    this_obj.$toasted.error('Error during Site loading ! Empty server reponse').goAway(5000);
                    return;
                }

                if (response.status === 200){
                    this_obj.$toasted.success('Site loaded !').goAway(1000);
                    let json_config = response.data.response_msg;
                    this_obj.code_site_blacklist_detect = json_config['blacklist_detection'];
                    this_obj.unhexed_regex = json_config['regex'];
                    
                }else{
                    this_obj.$toasted.error('Error during Site loading ! Code: ' + String(response.status)).goAway(5000);
                }

                return;
            })
            .catch(error =>{
                if (error === null ? 500 : error.response === null ? 500 : error.response.status === 404){
                    this_obj.$toasted.error('Site not found!').goAway(5000);
                    this_obj.$router.push('/');
                }else{
                    this_obj.$toasted.error('Error during Site loading ! error : ' + String(error)).goAway(5000);
                }
                return;
            });
        },

        save_site(){
            let this_obj = this;
            
            let payload = {};
            payload['site'] = {}
            payload['site']['regex'] = this_obj.unhexed_regex; 
            payload['site']['blacklist_detection'] = this_obj.code_site_blacklist_detect; 

            this.$store.axios_obj.post('/sites/update' ,payload, {
                headers: {
                    Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                }
            })
            .then(response =>{
                if (response === null){
                    this_obj.$toasted.error('Error during Site update ! Empty server reponse').goAway(5000);
                    return;
                }
                
                if (response.status === 200){
                    this_obj.$toasted.success('Site Saved !').goAway(1000);
                }else{
                    this_obj.$toasted.error('Error during Site update ! Code: ' + String(response.status)).goAway(5000);
                }

                return;
            })
            .catch(error =>{
                this_obj.$toasted.error('Error during Site update ! error : ' + String(error)).goAway(5000);
                return;
            });
        },

    },

    computed: {
        
    }
}

</script>
<style>
.prism-editor__container pre{
    color: #ccc !important;
}


.editor_config_headers_function {
    /* we dont use `language-` classes anymore so thats why we need to add background and text color manually */
    background: #2d2d2d;
    color: #ccc !important;

    /* you must provide font-family font-size line-height. Example: */
    font-family: Fira code, Fira Mono, Consolas, Menlo, Courier, monospace;
    font-size: 14px;
    line-height: 1.5;
    padding: 5px;
}

/* optional class for removing the outline */
.prism-editor__textarea:focus {
    outline: none;
}

.card{
    border : 3px !important;
}

.tdBreakWords{
    word-break: break-word;
}

.lander_main_component td{
    height: 10px !important;
    padding: 5px !important;
}

.card-header{
    padding: 0.45rem 1.25rem !important;
}

.btn-sm{
    padding: 4px !important;
}

.modal-title{
    font-size: 15px !important;
}

.modal-header{
    padding: 10px !important;
}

ul[role='tablist'].h-100{
    height: 80vh !important;
}
</style>