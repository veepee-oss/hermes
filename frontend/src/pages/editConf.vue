<template>
    <div v-if="!loading_main" class="lander_main_component">
        <div class="mb-3 card">
            <div class="no-gutters row">
                <div class="col-sm-6 col-md-12 col-xl-12">
                    <b-tabs pills card>
                        <b-tab title="Overall Config" active>
                            <b-card-text>
                                <div class="row" style="height: 40px;">
                                    <div class="col-6">
                                        <b>waterfall_requests</b>, <b>data_transformations</b>, <b>headers_freeze</b> and <b>headers</b> keys are not displayed here
                                    </div>
                                    <div class="col-6" style="text-align: right">
                                        <b-badge v-if="config_json_ok" variant="success">Syntax : OK</b-badge>
                                        <b-badge v-else variant="danger">Syntax : KO</b-badge>
                                    </div>
                                </div>
                                <div class="row" style="min-height: 400px; margin-top: 10px;">
                                    <div class="col-12">
                                        <prism-editor v-on:submit.prevent class="editor_config_json" v-model="code_config_json" :highlight="highlighter_json" line-numbers></prism-editor>
                                    </div>
                                </div>
                            </b-card-text>
                        </b-tab>
                        <template #tabs-end>
                            <b-nav-item href="#" @click="save_config" align="right">Save config</b-nav-item>
                        </template>

                        <b-tab title="Site Blacklist Response">
                            <b-card-text>
                                <div class="row" style="height: 40px;">
                                    <div class="col-8">
                                        The JS interpreter running this code is <b>Node</b>. It supports <b>Promises and Async functions</b>. Check doc for Syntax.                                       
                                    </div>
                                    <div class="col-4" style="text-align: right">
                                        <button v-on:click="gen_example_site_bl_response()" class="mt-1 btn btn-info btn-sm">Generate example code</button>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12">
                                        You may want to click on <b>Generate example code</b> to have a simple example with inputs explication
                                    </div>
                                </div>
                                <div class="row" style="min-height: 400px; margin-top: 10px;">
                                    <div class="col-12">
                                        <prism-editor v-on:submit.prevent class="editor_config_headers_function" v-model="code_site_site_blacklist_response" :highlight="highlighter_js" line-numbers></prism-editor>
                                    </div>
                                </div>
                            </b-card-text>
                        </b-tab>

                        <b-tab title="Proxy">
                            <b-card-text>
                                <div class="row" style="height: 40px;">
                                    <div class="col-8">
                                        <b-form-checkbox
                                            v-model="config_json_proxy_mode_simple"
                                            >
                                            use <b>Simple</b> mode
                                        </b-form-checkbox>

                                        <span v-if="config_json_proxy_mode_simple">This can be <b>null</b> or a Dictionnary (should have 4 keys: <b>host, port, username, password</b>).</span>
                                        <span v-else>The JS interpreter running this code is <b>Node</b>. It supports <b>Promises and Async functions</b>. Check doc for Syntax.</span>                                        
                                    </div>
                                    <div class="col-4" style="text-align: right">
                                        
                                        <button v-if="config_json_proxy_mode_simple" v-on:click="gen_example_plain_proxy_code()" class="mt-1 btn btn-info btn-sm" style="margin-right: 20px;">Generate vanilla conf</button>
                                        <button v-else v-on:click="gen_example_js_proxy_code()" class="mt-1 btn btn-info btn-sm" style="margin-right: 20px;">Generate example code</button>
                                        
                                        <span v-if="config_json_proxy_mode_simple">
                                            <b-badge v-if="config_json_proxy" variant="success">Syntax : OK</b-badge>
                                            <b-badge v-else variant="danger">Syntax : KO</b-badge>
                                        </span>
                                        <span v-else>
                                            <b-badge variant="warning">Syntax : N.A.</b-badge>
                                        </span>
                                    </div>
                                </div>
                                <div v-if="!config_json_proxy_mode_simple" class="row">
                                    <div class="col-12">
                                    When using the <b>advanced mode</b>, you should console.log a Stringified dictionnary with 5 keys: <b>host, port, username, password, data</b>
                                    </div>
                                </div>
                                <div class="row" style="min-height: 400px; margin-top: 10px;">
                                    <div class="col-12" >
                                        <prism-editor v-on:submit.prevent v-if="config_json_proxy_mode_simple" class="editor_config_json" v-model="code_config_proxy_plain" :highlight="highlighter_json" line-numbers></prism-editor>
                                        <prism-editor v-on:submit.prevent v-else class="editor_config_headers_function" v-model="code_config_proxy_advanced" :highlight="highlighter_js" line-numbers></prism-editor>
                                    </div>
                                </div>
                            </b-card-text>
                        </b-tab>
                        <b-tab title="Headers js function">
                            <b-card-text>
                                <div class="row" style="height: 40px;">
                                    <div class="col-8">
                                        This can be <b>null</b> or a <b>JS function</b>. <br>
                                        The JS interpreter running this code <b>does not support Promises</b> nor <b>Async</b> functions. It is just a <b>JS eval</b> light engine. 
                                    </div>
                                    <div class="col-4" style="text-align: right">
                                        
                                        <button v-on:click="gen_boilerplate()" class="mt-1 btn btn-info btn-sm" style="margin-right: 20px;">Generate boilerplate code</button>

                                        <b-badge v-if="config_json_headers_js" variant="success">Syntax : OK</b-badge>
                                        <b-badge v-else variant="danger">Syntax : KO</b-badge>
                                    </div>
                                </div>
                                <div class="row" style="min-height: 400px; margin-top: 10px;">
                                    <div class="col-12" >
                                        <prism-editor v-on:submit.prevent class="editor_config_headers_function" v-model="code_config_headers_function" :highlight="highlighter_js" line-numbers></prism-editor>
                                    </div>
                                </div>
                            </b-card-text>
                        </b-tab>
                        <b-tab title="Headers Freeze">
                            <b-card-text>
                                <div class="row" style="height: 40px;">
                                    <div class="col-4">
                                        This needs to be a list of Dictionnaries
                                    </div>
                                    <div class="col-8" style="text-align: right">
                                        
                                        <button v-on:click="gen_headers_freeze_example()" class="mt-1 btn btn-info btn-sm" style="margin-right: 20px;">Generate example conf.</button>

                                        <b-badge v-if="config_json_headers_freeze" variant="success">Syntax : OK</b-badge>
                                        <b-badge v-else variant="danger">Syntax : KO</b-badge>
                                    </div>
                                </div>
                                <div class="row" style="min-height: 400px; margin-top: 10px;">
                                    <div class="col-12" >
                                        <prism-editor v-on:submit.prevent class="editor_config_json" v-model="code_config_headers_freeze" :highlight="highlighter_json" line-numbers></prism-editor>
                                    </div>
                                </div>
                            </b-card-text>
                        </b-tab>
                        <b-tab title="Test Config">
                            <b-card-text  v-if="!test_curl_loading">
                                <div class="row">
                                    <div class="col-3" style="text-align: right; display: flex;  justify-content: center;  align-content: center;  flex-direction: column;">
                                        URL
                                    </div>
                                    <div class="col-9" style="text-align: left">
                                        <b-form-input v-model="test_url" placeholder="Enter URL"></b-form-input>
                                    </div>
                                </div>

                                <div class="row" style="margin-top: 10px;">
                                    <div class="col-3" style="text-align: right; display: flex;  justify-content: center;  align-content: center;  flex-direction: column;">
                                        Method
                                    </div>
                                    <div class="col-9" style="text-align: left">
                                        <b-form-select v-model="test_method" :options="test_method_options" style="margin-right: 10px;"></b-form-select>
                                    </div>
                                </div>

                                

                                <div class="row" style="margin-top: 10px;">
                                    <div class="col-3" style="text-align: right; display: flex;  justify-content: top;  align-content: top;  flex-direction: column;">
                                        Headers
                                    </div>
                                    <div class="col-9" style="text-align: left">
                                        <div class="row" style="margin-bottom: 10px;" v-for="header_i in test_headers" :key="header_i[0]">
                                            <div class="col-1" style="text-align: center">
                                                
                                            </div>
                                            <div class="col-3" style="text-align: right;">
                                                {{ header_i[0] }}
                                            </div>
                                            <div class="col-1" style="text-align: center">
                                                :
                                            </div>
                                            <div class="col-3" style="text-align: left">
                                                {{ header_i[1] }}
                                            </div>
                                            <div class="col-3" style="text-align: left; display: flex;  justify-content: center;  align-content: center;  flex-direction: column;">
                                                <i v-on:click="delete_test_header(header_i[0])" class="pe-7s-trash icon-gradient bg-strong-bliss" style="font-size: 22px; cursor: pointer; margin-left: 10px;" title="Delete Header"> </i>
                                            </div>
                                        </div>

                                        <div class="row" style="margin-bottom: 13px;">
                                            <div class="col-1" style="text-align: center">
                                                
                                            </div>
                                            <div class="col-3" style="text-align: right;">
                                                <b-form-input v-model="test_header_add_key" placeholder="Enter Header Key"></b-form-input>
                                            </div>
                                            <div class="col-1" style="text-align: center">
                                                :
                                            </div>
                                            <div class="col-3" style="text-align: left">
                                                <b-form-input v-model="test_header_add_value" placeholder="Enter Header Value"></b-form-input>
                                            </div>
                                            <div class="col-3" style="text-align: left; display: flex;  justify-content: center;  align-content: center;  flex-direction: column;">
                                                <i v-on:click="add_test_header" class="pe-7s-up-arrow icon-gradient bg-grow-early" style="font-size: 22px; cursor: pointer; margin-left: 10px;" title="Add new header"> </i>
                                            </div>
                                        </div>

                                        <div class="row" style="margin-bottom: 13px;">
                                            <div class="col-12" style="font-size: 12px;">
                                            Warning: the testing Tool adds these headers:<br>
                                            - User-Agent : python-requests/2.18.4 <br>
                                            - Accept-Encoding : gzip, deflate <br>
                                            - Accept : */* <br>
                                            You can either overwrite them or handle them in the config.
                                            </div>
                                        </div>
                                    </div>
                                </div>


                                <div class="row">
                                    <div class="col-3" style="text-align: right; display: flex;  justify-content: top;  align-content: top;  flex-direction: column;">
                                        Data
                                    </div>
                                    <div class="col-9" style="text-align: left">
                                        <b-form-textarea
                                            v-model="test_data"
                                            placeholder="Enter data payload to be send !"
                                            size="sm"
                                            rows="5"
                                        />
                                    </div>
                                </div>

                                <div class="row" style="margin-top: 20px;">
                                    <div class="col-12" style="text-align: center">
                                       <button type="button" class="btn btn-outline-dark" style="width: 80%; font-size: 18px;" v-on:click="test_curl()">Test CURL</button>
                                    </div>
                                </div>

                                <div v-if="test_reply_data!=''" class="row" style="margin-top: 20px;">
                                    <div class="col-3" style="text-align: right; display: flex;  justify-content: top;  align-content: top;  flex-direction: column;margin-top: 10px;">
                                        Response
                                    </div>
                                    <div class="col-9" style="text-align: left; background-color: rgb(240,240,240);">
                                        <div style='margin-top: 10px; margin-bottom: 10px; font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; word-break: break-word; max-height: 35vh; overflow-x: hidden;'>
                                        {{test_reply_data}}
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row" style="margin-top: 20px;">
                                    <div class="col-12" style="text-align: center">
                                        <xRayLog :xRayID="test_xrayID" />
                                    </div>
                                </div>
                            </b-card-text>
                            
                            <div v-else style="display: grid; place-items: center; ">
                                <div>
                                    <div class="d-flex justify-content-center align-items-center" style="height: 60vh !important; margin: 30px;">
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

                        </b-tab>
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

import xRayLog from './components/xRayLog';

export default {
    name: 'editConf',
    components: {
        PrismEditor, xRayLog
    },
    data: () => ({
        loading_main: false,

        code_config_json: '{}',
        code_config_headers_function: null,
        code_config_headers_freeze: '[]',

        config_json_proxy_mode_simple: true,
        code_config_proxy_plain: 'null',
        code_config_proxy_advanced: '',
        code_site_site_blacklist_response: '',

        // ----- Testing framwork !
        test_curl_loading: false, 
        test_url: 'https://api.ipify.org?format=json',

        test_method: 'GET',
        test_method_options: [
            { value: 'POST', text: 'POST' },
            { value: 'GET', text: 'GET' }
        ],
        
        test_headers: [
            ['Content-Type', 'application/json']
        ],

        test_header_add_key: '',
        test_header_add_value: '',

        test_data: '',

        test_reply_data: '',
        test_xrayID: ''
    }),
    mounted: function(){
        this.fetch_config(this.$route.query.config_id_url);
    },

    methods: {
        highlighter_json(code) {
            return highlight(code, languages.json); // languages.<insert language> to return html with markup
        },

        highlighter_js(code) {
            return highlight(code, languages.js); // languages.<insert language> to return html with markup
        },

        gen_boilerplate(){
            this.code_config_headers_function = "(function(data_attribute_stringified) { // do not change this line \n    var headers_obj = eval(data_attribute_stringified);  // do not change this line \n    return JSON.stringify([headers_obj[0]]); // make sure to JSON.stringify the end list \n})('DATA_ATTRIBUTE_INPUT')  // do not change this line";
        },

        gen_headers_freeze_example(){
            this.code_config_headers_freeze = JSON.stringify([
                            {
                                "host_regex": ".*amazon.*",
                                "headers" : ["cookie", "user-agent"],
                                "max_requests": 1000
                            }
                        ], null, 4);
        },

        gen_example_plain_proxy_code(){
            this.code_config_proxy_plain = JSON.stringify({
                            "host": "proxy.website.com",
                            "port": 8080,
                            "password": null,
                            "username": null,
                            "type":"http"
                        }, null, 4);
        },

        gen_example_js_proxy_code(){
            this.code_config_proxy_advanced = "console.log(\n\tJSON.stringify(\n\t\t\t{\n\t\t\t\t'port': 8080,\n\t\t\t\t'host': 'proxy.website.com', \n\t\t\t\t'password': null, \n\t\t\t\t'user': null, \n\t\t\t\t'type': 'http', \n\t\t\t\t'data': 'some data I want to pass ...'\n\t\t\t}\n\t\t)\n\t);";
        },

        gen_example_site_bl_response(){
            this.code_site_site_blacklist_response = `// --------------------------------------------------------- 
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
// Please here your code !
console.log(input_data['proxy']['log']['data_carried']);

`;
        },

        fetch_config(config_id){
            let this_obj = this;
            this.$store.axios_obj.get('/configs/get/' + String(config_id),{
                headers: {
                    Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                }
            })
            .then(response =>{
                if (response === null){
                    this_obj.$toasted.error('Error during Config loading ! Empty server reponse').goAway(5000);
                    return;
                }

                if (response.status === 200){
                    this_obj.$toasted.success('Config loaded !').goAway(1000);
                    let json_config = response.data.response_msg;
                    
                    //let waterfall_requests = JSON.parse(JSON.stringify(json_config['waterfall_requests']))
                    delete json_config['waterfall_requests'];

                    //let data_transformations = JSON.parse(JSON.stringify(json_config['data_transformations']))
                    delete json_config['data_transformations'];

                    let headers = JSON.parse(JSON.stringify(json_config['headers']));
                    delete json_config['headers'];


                    // Parse headers_freeze part
                    let headers_freeze = [];
                    if (json_config['headers_freeze'] !== undefined){
                        headers_freeze = JSON.parse(JSON.stringify(json_config['headers_freeze']));
                        delete json_config['headers_freeze'];
                    }
                    
                    this_obj.code_config_headers_freeze = JSON.stringify(headers_freeze, null, 4);

                    // Parse proxy part
                    if (json_config['proxy'] === undefined){
                        this_obj.config_json_proxy_mode_simple = true;
                        this_obj.code_config_proxy_plain = 'null';
                        this_obj.code_config_proxy_advanced = '';
                    }else{
                        let proxy_node = JSON.parse(JSON.stringify(json_config['proxy']));
                        delete json_config['proxy'];

                        if (proxy_node === null){
                            this_obj.config_json_proxy_mode_simple = true;
                            this_obj.code_config_proxy_plain = 'null';
                            this_obj.code_config_proxy_advanced = '';
                        }else{
                            let js_mode = false;
                            if (proxy_node['js_mode'] !== undefined){
                                js_mode = proxy_node['js_mode'];
                                delete proxy_node['js_mode'];
                            }
                            this_obj.config_json_proxy_mode_simple = !js_mode;

                            if (this_obj.config_json_proxy_mode_simple == true){
                                this_obj.code_config_proxy_plain = JSON.stringify(proxy_node, null, 4);
                                this_obj.code_config_proxy_advanced = '';
                            }else{
                                this_obj.code_config_proxy_plain = 'null';
                                this_obj.code_config_proxy_advanced = proxy_node['js_function'];
                            }
                        }
                    }

                    // Parse site BL response
                    if (json_config['site_blacklist_response'] === undefined){
                        this_obj.code_site_site_blacklist_response = '';
                    }else{
                        this_obj.code_site_site_blacklist_response = JSON.parse(JSON.stringify(json_config['site_blacklist_response']));
                        delete json_config['site_blacklist_response'];
                    }

                    // Push code in main window
                    this_obj.code_config_json = JSON.stringify(json_config, null, 4);

                    // Push code in main window
                    if (headers === null){
                        this_obj.code_config_headers_function = 'null';
                    }else{
                        this_obj.code_config_headers_function = headers;
                    }
                    
                    
                }else{
                    this_obj.$toasted.error('Error during Config loading ! Code: ' + String(response.status)).goAway(5000);
                }

                return;
            })
            .catch(error =>{
                if (error === null ? 500 : error.response === null ? 500 : error.response.status === 404){
                    this_obj.$toasted.error('Config not found!').goAway(5000);
                    this_obj.$router.push('/');
                }else{
                    this_obj.$toasted.error('Error during Config loading ! error : ' + String(error)).goAway(5000);
                }
                return;
            });
        },

        save_config(){
            if (this._config_json_ok() == false){
                this.$toasted.error('Could not store Config, check syntax !').goAway(5000);
                return;
            }

            if (this._config_json_headers_js() == false){
                this.$toasted.error('Could not store Headers JS function, check syntax !').goAway(5000);
                return;
            }

            if (this._config_json_headers_freeze() == false){
                this.$toasted.error('Could not store Headers Freeze payload, check syntax !').goAway(5000);
                return;
            }

            if (this._config_json_proxy() == false){
                this.$toasted.error('Could not store Proxy payload, check syntax !').goAway(5000);
                return;
            }

            

            let this_obj = this;

            
            let payload = {};

            try {    
                payload['config'] = JSON.parse(this_obj.code_config_json);
                payload['config']['data_transformations'] = []; // not coded yet
                payload['config']['waterfall_requests'] = []; // not coded yet
                payload['config']['headers_freeze'] = JSON.parse(this_obj.code_config_headers_freeze);

                // Handle Proxy part
                if (this_obj.config_json_proxy_mode_simple){
                    if (String(this_obj.code_config_proxy_plain).toLowerCase() == 'null'){
                        payload['config']['proxy'] = null;
                    }else{
                        payload['config']['proxy'] = JSON.parse(this_obj.code_config_proxy_plain);
                        payload['config']['proxy']['js_mode'] = false;
                    }
                }else{
                    payload['config']['proxy'] = {};
                    payload['config']['proxy']['js_mode'] = true;
                    payload['config']['proxy']['js_function'] = String(this_obj.code_config_proxy_advanced);
                }

                // Handle site BL response
                payload['config']['site_blacklist_response'] = String(this_obj.code_site_site_blacklist_response);

                // Handle Headers part
                if (String(this.code_config_headers_function).toLowerCase() == 'null'){
                    payload['config']['headers'] = null;
                }else{
                    payload['config']['headers'] = String(this.code_config_headers_function);
                }
                 
            } catch (error) {
                this_obj.$toasted.error('Could not store Config, check syntax !').goAway(5000);
                return;
            }

            this.$store.axios_obj.post('/configs/update/' + String(this.$route.query.config_id_url),payload, {
                headers: {
                    Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                }
            })
            .then(response =>{
                if (response === null){
                    this_obj.$toasted.error('Error during Config update ! Empty server reponse').goAway(5000);
                    return;
                }
                
                if (response.status === 200){
                    this_obj.$toasted.success('Config Saved !').goAway(1000);
                }else{
                    this_obj.$toasted.error('Error during Config update ! Code: ' + String(response.status)).goAway(5000);
                }

                return;
            })
            .catch(error =>{
                this_obj.$toasted.error('Error during Config update ! error : ' + String(error)).goAway(5000);
                return;
            });
        },

        delete_test_header(test_header_key){
            let new_test_headers = [];
            for (var i = 0; i < this.test_headers.length; i++) {
                if (this.test_headers[i][0] != test_header_key){
                    new_test_headers.push([this.test_headers[i][0], this.test_headers[i][1]]);
                }
            }
            this.test_headers = new_test_headers;
        },

        add_test_header(){
            if ((this.test_header_add_key == "") || (this.test_header_add_value == "")){
                this.$toasted.error('Empty values !').goAway(5000);
            }else{
                this.test_headers.push([this.test_header_add_key, this.test_header_add_value]);
                this.test_header_add_key = '';
                this.test_header_add_value = '';
            }
        },

        test_curl(){
            let this_obj = this;

            this_obj.test_curl_loading = true;
            this_obj.test_reply_data = '';
            this_obj.test_xrayID = '';
            
            let payload = {};
            payload['url'] = this_obj.test_url;
            payload['method'] = this_obj.test_method;
            payload['headers'] = this_obj.test_headers;
            payload['data'] = this_obj.test_data;
            payload['config_id'] = this.$route.query.config_id_url;
            
            
            this_obj.$store.axios_obj({
                method: 'post',
                url: this_obj.$store.axios_obj.defaults.baseURL + '/test_curl',
                timeout: 120 * 1000, // 120 secs
                data: payload,
                headers: {
                    Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                }
            })
            .then(response =>{
                if (response === null){
                    this_obj.$toasted.error('Error during Test ! Empty server reponse').goAway(5000);
                    this_obj.test_curl_loading = false;
                    return;
                }

                if (response.status === 200){
                    if (response.data.response_code === true){
                        this_obj.test_reply_data = response.data.response_msg.response;
                        this_obj.$toasted.success('Test ended !').goAway(1000);
                    }else{
                        this_obj.test_reply_data = 'Error message: ' + response.data.response_msg.response;
                        this_obj.$toasted.error('Request failed !').goAway(5000);
                    }

                    this_obj.test_xrayID = response.data.response_msg.xray_token;
                    
                }else{
                    this_obj.$toasted.error('Error during Test ! Code: ' + String(response.status)).goAway(5000);
                }
                
                this_obj.test_curl_loading = false;
                return;
            })
            .catch(error =>{
                this_obj.$toasted.error('Error during Test ! error : ' + String(error)).goAway(5000);
                this_obj.test_curl_loading = false;
                return;
            });

            
        },

        _config_json_ok: function(){
            try {
                JSON.parse(this.code_config_json);
                return true;
            } catch (error) {
                return false;
            }
        },

        _config_json_headers_js: function(){
            if (String(this.code_config_headers_function).toLowerCase() == 'null'){
                return true;
            }else{
                try {
                    JSON.parse(eval(this.code_config_headers_function.replace('DATA_ATTRIBUTE_INPUT','[["key","value"]]'))).length;
                    return true;
                } catch (error) {
                    return false;
                }
            }
        },

        _config_json_headers_freeze: function(){
            try {
                let conf_freeze = JSON.parse(this.code_config_headers_freeze);
                
                if (Array.isArray(conf_freeze)) {
                    for (var i = 0; i < conf_freeze.length; i++) {
                        let node_i = conf_freeze[i];

                        if (node_i['headers'] === undefined) {
                            return false;
                        }

                        if (node_i['host_regex'] === undefined) {
                            return false;
                        }

                        if (node_i['max_requests'] === undefined) {
                            return false;
                        }

                        if (Array.isArray(node_i['headers']) === false) {
                            return false;
                        }

                        if (Number.isInteger(node_i['max_requests']) === false){
                            return false;
                        }
                    }
                    return true;
                }else{
                    return false;
                }                
            } catch (error) {
                return false;
            }
        },

        _config_json_proxy: function(){
            if (this.config_json_proxy_mode_simple){
                // Simple mode !
                if (String(this.code_config_proxy_plain).toLowerCase() == 'null'){
                    // None !
                    return true;
                }else{
                    // A real node !
                    try {
                        let proxy_node = JSON.parse(this.code_config_proxy_plain);
                        
                        if (proxy_node['port'] === undefined) {
                            return false;
                        }

                        if (proxy_node['host'] === undefined) {
                            return false;
                        }

                        if (proxy_node['password'] === undefined) {
                            return false;
                        }

                        if (proxy_node['username'] === undefined) {
                            return false;
                        }

                        if (Number.isInteger(proxy_node['port']) === false){
                            return false;
                        }

                        return true;
                    } catch (error) {
                        return false;
                    }
                }
            }else{
                // Js mode !
                return true;
            }
        }
    },

    computed: {
        config_json_ok: function(){
            return this._config_json_ok();
        },

        config_json_headers_js: function(){
            return this._config_json_headers_js();
        },

        config_json_headers_freeze: function(){
            return this._config_json_headers_freeze();
        },

        config_json_proxy: function(){
            return this._config_json_proxy();
        }
    }
}

</script>
<style>
.prism-editor__container pre{
    color: #ccc !important;
}

.editor_config_json {
    /* we dont use `language-` classes anymore so thats why we need to add background and text color manually */
    background: #2d2d2d;
    color: #ccc !important;

    /* you must provide font-family font-size line-height. Example: */
    font-family: Fira code, Fira Mono, Consolas, Menlo, Courier, monospace;
    font-size: 14px;
    line-height: 1.5;
    padding: 5px;
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