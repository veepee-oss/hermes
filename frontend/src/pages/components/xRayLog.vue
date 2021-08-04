<template>
    <div v-if="xRayID!=''">
        <div class="row">
            <div class="col-3" style="text-align: right; display: flex;  justify-content: center;  align-content: center;  flex-direction: column;">
                xRayId
            </div>
            <div class="col-9" style="text-align: left">
                <b-form-input disabled v-model="xRayID" placeholder="Enter URL"></b-form-input>
            </div>
        </div>
        <div class="row" style="margin-top: 20px;">
            <div class="col-12">
                <b-table :striped="striped"
                    :bordered="bordered"
                    :outlined="outlined"
                    :small="small"
                    :hover="hover"
                    :dark="dark"
                    :fixed="fixed"
                    :foot-clone="footClone"
                    :items="list_logs"
                    :fields="fields"
                    :per-page="perPage"
                    :current-page="currentPage">
                    <template #cell(tag)="data">
                        <b-badge v-if="data.item.tag === 'ERROR'" variant="danger">ERROR</b-badge>
                        <b-badge v-else-if="data.item.tag === 'SUCCESS'" variant="success">SUCCESS</b-badge>
                        <b-badge v-else variant="dark">INFO</b-badge>
                    </template>

                    <template #cell(date)="data">
                        <i>{{data.item.date}}</i>
                    </template>

                    <template #cell(details)="data">
                        <div class="row">
                            <div class="col" style="font-size: 17px;">
                                {{data.item.message.replace(data.item.date + ' ','')}}
                            </div>
                        </div>

                        <div class="row" style="margin-top: 5px;">
                            <div class="col">
                                <span v-if="Object.keys(data.item.data).length == 0" style="font-size: 12px">no data ...</span>
                                <vue-json-pretty :deep="deepComputed(data.item.message)" :showLine="showLine" v-else :data="parseBson(data.item.data)"> </vue-json-pretty>
                            </div>
                        </div>
                    </template>


                    <b-badge variant="danger">Danger</b-badge>
                </b-table>
            </div>
        </div>
        
    </div>
</template>

<script>
    import VueJsonPretty from 'vue-json-pretty';
    import bson_converter_lib from '../../libs/bson_converter.js'

    export default {
        name: "xRayLog",
        props: ['xRayID'],
        components: {
            VueJsonPretty
        },

        data() {
            return {
                striped: true,
                bordered: true,
                outlined: true,
                small: false,
                hover: true,
                dark: false,
                fixed: true,
                footClone: false,
                showLine:false,

                perPage: 100,
                currentPage: 1,

                fields : ['tag','date',{ key: "details", tdClass: "tdBreakWordsxRay" }],
                list_logs: []
            }
        },
        mounted: function(){
            let this_obj = this;
            this.$store.axios_obj.post('/logs/fetch_xray_log', {"xrayID": String(this_obj.xRayID)}, {
                headers: {
                    Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                }
            })
            .then(response =>{
                this_obj.$toasted.success('xRays loaded !').goAway(1000);
                this_obj.list_logs =  response.data;
            })
            .catch(error =>{
                this_obj.$toasted.error('Error during XRAY loads : ' + String(error)).goAway(5000);
            });
        },
        methods: {
            parseBson: function(input_val){
                const bson_converter_lib_obj = new bson_converter_lib();
                let res = bson_converter_lib_obj.decode_json(input_val);
                if ('reply' in res){
                    if (res['reply'].length > 100000){
                        res['reply'] = res['reply'].substring(0, 100000) + ' ... (truncated)';
                    }
                }
                return res;
            },
            deepComputed: function(message_log){
                if (message_log.includes('Step 4.')){
                    return Infinity;
                }else{
                    return 0;
                }
            }
        }
    };
</script>

<style>
.tdBreakWordsxRay{
    word-break: break-word;
    text-align: left !important;
}

</style>
