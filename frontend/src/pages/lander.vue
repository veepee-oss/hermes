<template>
    <div v-if="!loading_main" class="lander_main_component">
        <div class="mb-3 card">
            <div class="card-header-tab card-header">
                <div class="card-header-title font-size-lg text-capitalize font-weight-normal row">
                    <div class="col">
                        <i class="header-icon lnr-charts icon-gradient bg-happy-green"> </i>
                        Weekly Summary
                    </div>
                    <div class="col" style="text-align: right">
                        <button v-on:click="$bvModal.show('bv_modal_flush_cache')" class="mt-1 btn btn-warning btn-sm" style="margin-right: 14px;">Flush stats</button>
                        <button v-on:click="reload_page(false)" class="mt-1 btn btn-info btn-sm">Refresh</button>
                    </div>
                </div>
            </div>
            <div class="no-gutters row">
                <div class="col-sm-6 col-md-3 col-xl-3">
                    <div class="card no-shadow rm-border bg-transparent widget-chart text-left">
                        <div class="icon-wrapper rounded-circle">
                            <div class="icon-wrapper-bg opacity-10 bg-warning"></div>
                            <i class="pe-7s-repeat text-white opacity-8"></i></div>
                        <div class="widget-chart-content">
                            <div class="widget-subheading">Requests</div>
                            <div class="widget-numbers">{{main_kpis_req}}</div>
                        </div>
                    </div>
                </div>
                <div class="col-sm-6 col-md-3 col-xl-3">
                    <div class="card no-shadow rm-border bg-transparent widget-chart text-left">
                        <div class="icon-wrapper rounded-circle">
                            <div class="icon-wrapper-bg opacity-10 bg-success"></div>
                            <i class="pe-7s-paper-plane text-white opacity-8"></i></div>
                        <div class="widget-chart-content">
                            <div class="widget-subheading">Success</div>
                            <div class="widget-numbers">{{main_kpis_success}}</div>
                        </div>
                    </div>
                </div>
                <div class="col-sm-6 col-md-3 col-xl-3">
                    <div class="card no-shadow rm-border bg-transparent widget-chart text-left">
                        <div class="icon-wrapper rounded-circle">
                            <div class="icon-wrapper-bg opacity-10 bg-danger"></div>
                            <i class="pe-7s-cloud-download text-white opacity-8"></i></div>
                        <div class="widget-chart-content">
                            <div class="widget-subheading">Bandwidth</div>
                            <div class="widget-numbers">{{main_kpis_bw}}</div>
                        </div>
                    </div>
                </div>
                <div class="col-sm-6 col-md-3 col-xl-3">
                    <div class="card no-shadow rm-border bg-transparent widget-chart text-left">
                        <div class="icon-wrapper rounded-circle">
                            <div class="icon-wrapper-bg opacity-10 bg-alternate"></div>
                            <i class="pe-7s-tools text-white opacity-8"></i></div>
                        <div class="widget-chart-content">
                            <div class="widget-subheading">Configs</div>
                            <div class="widget-numbers">{{main_kpis_confs}}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>


        <!-- ------------------------------ -->
        <div class="row">
            <div class="col-sm-12 col-lg-8">
                <div class="mb-3 card">
                    <div class="card-header-tab card-header">
                        <div class="card-header-title font-size-lg text-capitalize font-weight-normal">
                            <i class="header-icon lnr-cloud-download icon-gradient bg-happy-itmeo"> </i>
                            Configs stats
                        </div>
                    </div>
                    <div class="p-0 card-body">
                        <b-card class="main-card mb-4" style="min-height: 500px !important; margin-bottom: 0px !important;">
                            <div class="row">
                                <div class="col" style="text-align: left">
                                    <b-pagination
                                        style="text-align: left;"
                                        v-model="config_stats_table.currentPage"
                                        :total-rows="config_stats_table_rows"
                                        :per-page="config_stats_table.perPage"
                                        aria-controls="my-table"
                                        align="left"
                                        size="sm"
                                        >
                                    </b-pagination>
                                </div>

                                <div class="col" style="text-align: right">
                                    <button v-on:click="new_config()" class="mt-1 btn btn-success btn-sm" style="margin-right: 14px;">New config</button>
                                    <button v-on:click="reload_page(false)" class="mt-1 btn btn-info btn-sm">Refresh</button>
                                </div>
                            </div>
                            

                            <div class="row">
                                <div class="col" style="min-height: 350px !important;  font-size: 12px !important">
                                    <b-table :striped="striped"
                                        :bordered="bordered"
                                        :outlined="outlined"
                                        :small="small"
                                        :hover="hover"
                                        :dark="dark"
                                        :fixed="fixed"
                                        :foot-clone="footClone"
                                        :items="config_stats_table.items"
                                        :fields="config_stats_table.fields"
                                        :per-page="config_stats_table.perPage"
                                        :current-page="config_stats_table.currentPage">
                                        <template #cell(edit)="data">
                                            <router-link :to="'/editconfig?config_id_url=' + String(data.item.id)" class="nav-link title_bar" style="padding: 0px !important">
                                                <i class="pe-7s-edit icon-gradient bg-grow-early" style="font-size: 12px;" title="Edit"> </i>
                                            </router-link>
                                        </template>

                                        <template #cell(del)="data"><i v-on:click="delete_config(data.item.id)" class="pe-7s-trash icon-gradient bg-strong-bliss" style="font-size: 12px; cursor: pointer;" title="Delete"> </i>
                                        </template>
                                </b-table>
                                </div>
                            </div>
                            

                            <b-pagination
                                style="text-align: left;"
                                v-model="config_stats_table.currentPage"
                                :total-rows="config_stats_table_rows"
                                :per-page="config_stats_table.perPage"
                                aria-controls="my-table"
                                align="left"
                                size="sm"
                                >
                            </b-pagination>
                        </b-card>
                    </div>
                </div>
            </div>
            <div class="col-sm-12 col-lg-4">
                <div class="card-hover-shadow-2x mb-3 card">
                    <div class="card-header-tab card-header">
                        <div class="card-header-title font-size-lg text-capitalize font-weight-normal">
                            <i class="header-icon lnr-lighter icon-gradient bg-amy-crisp"> </i>
                            Protocols & Domains
                        </div>
                    </div>
                    <div class="p-0 card-body">
                        <b-card class="main-card mb-4" style="min-height: 500px !important; margin-bottom: 0px !important;">
                            <div class="row">
                                <div class="col" style="font-size: 12px !important">
                                    <b-table :striped="striped"
                                            :bordered="bordered"
                                            :outlined="outlined"
                                            :small="small"
                                            :hover="hover"
                                            :dark="dark"
                                            :fixed="fixed"
                                            :foot-clone="footClone"
                                            :items="protocol_protocol_table.items"
                                            :fields="protocol_protocol_table.fields"
                                            :per-page="protocol_protocol_table.perPage"
                                            :current-page="protocol_protocol_table.currentPage">
                                    </b-table>
                                </div>
                            </div>

                            <div class="row" style="margin-top: 30px; margin-bottom: 0px;">
                                <div class="col" style="font-size: 12px !important">
                                    <b-table :striped="striped"
                                            :bordered="bordered"
                                            :outlined="outlined"
                                            :small="small"
                                            :hover="hover"
                                            :dark="dark"
                                            :fixed="fixed"
                                            :foot-clone="footClone"
                                            :items="domain_protocol_table.items"
                                            :fields="domain_protocol_table.fields"
                                            :per-page="domain_protocol_table.perPage"
                                            :current-page="domain_protocol_table.currentPage">
                                    </b-table>
                                </div>
                            </div>
                            
                        </b-card>
                    </div>
                </div>
            </div>
        </div>



        <div class="row">
            <div class="col-sm-12 col-lg-7">
                <div class="mb-3 card">
                    <div class="card-header-tab card-header">
                        <div class="card-header-title font-size-lg text-capitalize font-weight-normal">
                            <i class="header-icon lnr-cloud-download icon-gradient bg-happy-itmeo"> </i>
                            Sites
                        </div>
                    </div>
                    <div class="p-0 card-body">
                        <b-card class="main-card mb-4" style="min-height: 500px !important; margin-bottom: 0px !important;">
                            <div class="row">
                                <div class="col" style="text-align: left">
                                    <b-pagination
                                        style="text-align: left;"
                                        v-model="sites_stats_table.currentPage"
                                        :total-rows="sites_stats_table_rows"
                                        :per-page="sites_stats_table.perPage"
                                        aria-controls="my-table"
                                        align="left"
                                        size="sm"
                                        >
                                    </b-pagination>
                                </div>

                                <div class="col" style="text-align: right">
                                    <button v-on:click="new_site()" class="mt-1 btn btn-success btn-sm" style="margin-right: 14px;">New site</button>
                                    <button v-on:click="reload_page(false)" class="mt-1 btn btn-info btn-sm">Refresh</button>
                                </div>
                            </div>
                            

                            <div class="row">
                                <div class="col" style="min-height: 350px !important;  font-size: 12px !important">
                                    <b-table :striped="striped"
                                        :bordered="bordered"
                                        :outlined="outlined"
                                        :small="small"
                                        :hover="hover"
                                        :dark="dark"
                                        :fixed="fixed"
                                        :foot-clone="footClone"
                                        :items="sites_stats_table.items"
                                        :fields="sites_stats_table.fields"
                                        :per-page="sites_stats_table.perPage"
                                        :current-page="sites_stats_table.currentPage">
                                        <template #cell(edit)="data">
                                            <router-link :to="'/editsite?site_hex=' + String(data.item.site_hex)" class="nav-link title_bar" style="padding: 0px !important">
                                                <i class="pe-7s-edit icon-gradient bg-grow-early" style="font-size: 12px;" title="Edit"> </i>
                                            </router-link>
                                        </template>

                                        <template #cell(del)="data"><i v-on:click="delete_site(data.item.site_hex)" class="pe-7s-trash icon-gradient bg-strong-bliss" style="font-size: 12px; cursor: pointer;" title="Delete"> </i>
                                        </template>
                                </b-table>
                                </div>
                            </div>
                            

                            <b-pagination
                                style="text-align: left;"
                                v-model="config_stats_table.currentPage"
                                :total-rows="config_stats_table_rows"
                                :per-page="config_stats_table.perPage"
                                aria-controls="my-table"
                                align="left"
                                size="sm"
                                >
                            </b-pagination>
                        </b-card>
                    </div>
                </div>
            </div>
            <div class="col-sm-12 col-lg-5">
                <div class="card-hover-shadow-2x mb-3 card">
                    <div class="card-header-tab card-header">
                        <div class="card-header-title font-size-lg text-capitalize font-weight-normal">
                            <i class="header-icon lnr-lighter icon-gradient bg-amy-crisp"> </i>
                            Highest blacklists
                        </div>
                    </div>
                    <div class="p-0 card-body">
                        <b-card class="main-card mb-4" style="min-height: 500px !important; margin-bottom: 0px !important;">
                            <div class="row">
                                <div class="col" style="text-align: left">
                                    <b-pagination
                                        style="text-align: left;"
                                        v-model="sites_configs_stats_table.currentPage"
                                        :total-rows="sites_configs_stats_table_rows"
                                        :per-page="sites_configs_stats_table.perPage"
                                        aria-controls="my-table"
                                        align="left"
                                        size="sm"
                                        >
                                    </b-pagination>
                                </div>

                                <div class="col" style="text-align: right">
                                    <button v-on:click="reload_page(false)" class="mt-1 btn btn-info btn-sm">Refresh</button>
                                </div>
                            </div>
                            

                            <div class="row">
                                <div class="col" style="min-height: 350px !important;  font-size: 12px !important">
                                    <b-table :striped="striped"
                                        :bordered="bordered"
                                        :outlined="outlined"
                                        :small="small"
                                        :hover="hover"
                                        :dark="dark"
                                        :fixed="fixed"
                                        :foot-clone="footClone"
                                        :items="sites_configs_stats_table.items"
                                        :fields="sites_configs_stats_table.fields"
                                        :per-page="sites_configs_stats_table.perPage"
                                        :current-page="sites_configs_stats_table.currentPage">
                                </b-table>
                                </div>
                            </div>
                            

                            <b-pagination
                                style="text-align: left;"
                                v-model="config_stats_table.currentPage"
                                :total-rows="config_stats_table_rows"
                                :per-page="config_stats_table.perPage"
                                aria-controls="my-table"
                                align="left"
                                size="sm"
                                >
                            </b-pagination>
                        </b-card>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-sm-12 col-lg-12">
                <div class="mb-3 card">
                    <div class="card-header-tab card-header">
                        <div class="card-header-title font-size-lg text-capitalize font-weight-normal">
                            <i class="header-icon lnr-cloud-download icon-gradient bg-happy-itmeo"> </i>
                            Last requests
                        </div>
                    </div>
                    <div class="p-0 card-body">
                        <b-card class="main-card mb-4" style="margin-bottom: 0px !important;">
                            
                            

                            <div class="row">
                                <div class="col" style="text-align: left">
                                    <b-pagination
                                        style="text-align: left;"
                                        v-model="last_requests_table.currentPage"
                                        :total-rows="last_requests_table_rows"
                                        :per-page="last_requests_table.perPage"
                                        aria-controls="my-table"
                                        align="left"
                                        size="sm"
                                        >
                                    </b-pagination>
                                </div>

                            

                                <div class="col" style="text-align: right">
                                    <b-form-select v-model="selectedFilterConfig" v-on:change="reload_page(false)" :options="optionsFilterConfig" style="margin-right: 10px; width: 300px;"></b-form-select>
                                    <button v-on:click="reload_page(false)" class="mt-1 btn btn-info btn-sm">Refresh</button>
                                </div>
                            </div>
                            
                            
                            <div class="row">
                                <div class="col" style="min-height: 620px !important; font-size: 12px !important">
                                    <b-table :striped="striped"
                                            :bordered="bordered"
                                            :outlined="outlined"
                                            :small="small"
                                            :hover="hover"
                                            :dark="dark"
                                            :fixed="fixed"
                                            :foot-clone="footClone"
                                            :items="last_requests_table.items"
                                            :fields="last_requests_table.fields"
                                            :per-page="last_requests_table.perPage"
                                            :current-page="last_requests_table.currentPage">
                                            <template #cell(details)="data">
                                                <i v-on:click="more_details_req(data.item)" class="pe-7s-menu icon-gradient bg-plum-plate" style="font-size: 22px; cursor: pointer" title="Details"> </i>
                                            </template>
                                    </b-table>
                                </div>
                            </div>

                            <b-pagination
                                style="text-align: left;"
                                v-model="last_requests_table.currentPage"
                                :total-rows="last_requests_table_rows"
                                :per-page="last_requests_table.perPage"
                                aria-controls="my-table"
                                align="left"
                                size="sm"
                                >
                            </b-pagination>
                        </b-card>
                    </div>
                </div>
            </div>
        </div>
        
        <b-modal  size="xl" id="bv_modal_show_req" ref="bv_modal_show_req" hide-footer>
            <template #modal-title>
                Requests details
            </template>
            <div class="d-block text-center">
                <b-card no-body>
                    <b-tabs pills card vertical>
                        <b-tab title="Connect Request" active>
                            <b-card-text style="height: 65vh; overflow-x: hidden;">
                                <div class="row">
                                    <div class="col-3" style="text-align:right">
                                        <b>Connection</b>
                                    </div>
                                    <div class="col-9" style="text-align:left">
                                        <vue-json-pretty :path="'res'" :data="modal_zoom_req == null ? {} : modal_zoom_req.req_connect == null ? {} : modal_zoom_req.req_connect.connection == null ? {} : modal_zoom_req.req_connect.connection"> </vue-json-pretty>
                                    </div>
                                </div>
                                <div class="row" style="margin-top: 20px;">
                                    <div class="col-3" style="text-align:right">
                                        <b>Headers</b>
                                    </div>
                                    <div class="col-9" style="text-align:left">
                                        <div style="margin-bottom: 3px;" class="row" v-for="item in modal_zoom_req == null ? [] : modal_zoom_req.req_connect == null ? [] : modal_zoom_req.req_connect.headers == null ? {} : modal_zoom_req.req_connect.headers" :key="item[0]">
                                            <div class="col-3" style="text-align:right">
                                                <i>{{item[0]}}</i>
                                            </div>
                                            <div class="col-9" style="text-align:left">
                                                {{item[1]}}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row" style="margin-top: 20px;">
                                    <div class="col-3" style="text-align:right">
                                        <b>request_uri</b>
                                    </div>
                                    <div class="col-9" style="text-align:left">
                                        <vue-json-pretty :path="'res'" :data="modal_zoom_req == null ? {} : modal_zoom_req.req_connect == null ? {} : modal_zoom_req.req_connect.request_uri == null ? {} : modal_zoom_req.req_connect.request_uri"> </vue-json-pretty>
                                    </div>
                                </div>
                                <div class="row" style="margin-top: 20px;">
                                    <div class="col-3" style="text-align:right">
                                        <b>data</b>
                                    </div>
                                    <div class="col-9" style="text-align:left">
                                        {{modal_zoom_req == null ? {} : modal_zoom_req.req_connect == null ? {} : modal_zoom_req.req_connect.data == null ? {} : modal_zoom_req.req_connect.data}}
                                    </div>
                                </div>
                            </b-card-text>
                        </b-tab>
                        <b-tab title="Data Request">
                            <b-card-text style="height: 65vh; overflow-x: hidden;">
                                <div class="row">
                                    <div class="col-3" style="text-align:right">
                                        <b>Connection</b>
                                    </div>
                                    <div class="col-9" style="text-align:left">
                                        <vue-json-pretty :path="'res'" :data="modal_zoom_req == null ? {} : modal_zoom_req.req_data == null ? {} : modal_zoom_req.req_data.connection == null ? {} : modal_zoom_req.req_data.connection"> </vue-json-pretty>
                                    </div>
                                </div>
                                <div class="row" style="margin-top: 20px;">
                                    <div class="col-3" style="text-align:right">
                                        <b>Headers</b>
                                    </div>
                                    <div class="col-9" style="text-align:left">
                                        <div style="margin-bottom: 3px;" class="row" v-for="item in modal_zoom_req == null ? [] : modal_zoom_req.req_data == null ? [] : modal_zoom_req.req_data.headers == null ? {} : modal_zoom_req.req_data.headers" :key="item[0]">
                                            <div class="col-3" style="text-align:right">
                                                <i>{{item[0]}}</i>
                                            </div>
                                            <div class="col-9" style="text-align:left">
                                                {{item[1]}}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row" style="margin-top: 20px;">
                                    <div class="col-3" style="text-align:right">
                                        <b>request_uri</b>
                                    </div>
                                    <div class="col-9" style="text-align:left">
                                        <vue-json-pretty :path="'res'" :data="modal_zoom_req == null ? {} : modal_zoom_req.req_data == null ? {} : modal_zoom_req.req_data.request_uri == null ? {} : modal_zoom_req.req_data.request_uri"> </vue-json-pretty>
                                    </div>
                                </div>
                                <div class="row" style="margin-top: 20px;">
                                    <div class="col-3" style="text-align:right">
                                        <b>data</b>
                                    </div>
                                    <div class="col-9" style="text-align:left">
                                        {{modal_zoom_req == null ? {} : modal_zoom_req.req_data == null ? {} : modal_zoom_req.req_data.data == null ? {} : modal_zoom_req.req_data.data}}
                                    </div>
                                </div>
                            </b-card-text>
                        </b-tab>
                        <b-tab title="Reply">
                            <b-card-text style="height: 65vh; overflow-x: hidden;">
                                <div class="row">
                                    <div class="col-3" style="text-align:right">
                                        <b>Reply</b>
                                    </div>
                                    <div class="col-9" style="text-align:left">
                                        <vue-json-pretty :path="'res'" :data="modal_zoom_req == null ? {} : modal_zoom_req.reply == null ? {} : modal_zoom_req.reply"> </vue-json-pretty>
                                    </div>
                                </div>
                            </b-card-text>
                        </b-tab>
                    </b-tabs>
                </b-card>
            </div>
            <!--<b-button class="mt-3" block @click="$bvModal.hide('bv_modal_show_req')">Close Me</b-button>-->
        </b-modal>

        <b-modal
            id="bv_modal_flush_cache"
            ref="bv_modal_flush_cache"
            title="Confirm Cache Flush ?"
            @show="closeModal('bv_modal_flush_cache')"
            @hidden="closeModal('bv_modal_flush_cache')"
            @ok="_flush_cache_confirm"
        >
            Really want to Flush stats ?
        </b-modal>

        <b-modal
            id="modal_config_delete"
            ref="modal_config_delete"
            title="Confirm config deletion ?"
            @show="closeModal('modal_config_delete')"
            @hidden="closeModal('modal_config_delete')"
            @ok="_delete_config_confirm"
        >
            Really want to delete this config_id : <b>{{conf_flagged_for_del}}</b> for ever ?
        </b-modal>

        <b-modal
            id="modal_site_delete"
            ref="modal_site_delete"
            title="Confirm site deletion ?"
            @show="closeModal('modal_site_delete')"
            @hidden="closeModal('modal_site_delete')"
            @ok="_delete_site_confirm"
        >
            Really want to delete this site_hex : <b>{{site_flagged_for_del}}</b> for ever ?
        </b-modal>

        <b-modal
            id="modal_new_config"
            ref="modal_new_config"
            title="Create new config"
            @show="closeModal('modal_new_config')"
            @hidden="closeModal('modal_new_config')"
            @ok="storeNewConfig"
        >
            <form ref="form" @submit.stop.prevent="handleSubmit">
                <b-form-group
                label="Config name"
                label-for="name-input"
                invalid-feedback="Name is required"
                :state="configNewNameState"
                >
                <b-form-input
                    id="name-input"
                    v-model="configNewName"
                    :state="configNewNameState"
                    required
                ></b-form-input>
                </b-form-group>
            </form>
        </b-modal>


        <b-modal
            id="modal_new_site"
            ref="modal_new_site"
            title="Create new site"
            @show="closeModal('modal_new_site')"
            @hidden="closeModal('modal_new_site')"
            @ok="storeNewSite"
        >
            <form ref="form" @submit.stop.prevent="handleSubmit">
                <b-form-group
                label="Site Regex"
                label-for="regex-input"
                invalid-feedback="Regex is required"
                :state="siteNewRegexState"
                >
                <b-form-input
                    id="name-input"
                    v-model="siteNewRegex"
                    :state="siteNewRegexState"
                    required
                ></b-form-input>
                </b-form-group>
            </form>
        </b-modal>
        
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
    import bson_converter_lib from '../libs/bson_converter.js'

    import VueJsonPretty from 'vue-json-pretty';
    import 'vue-json-pretty/lib/styles.css';

    export default {
        name: 'lander',
        components: {
            VueJsonPretty
        },
        data: () => ({
            heading: 'Analytics Dashboard',
            subheading: 'This is an example dashboard created using build-in elements and components.',
            icon: 'pe-7s-plane icon-gradient bg-tempting-azure',

            loading_main: true,

            striped: true,
            bordered: true,
            outlined: true,
            small: false,
            hover: true,
            dark: false,
            fixed: true,
            footClone: false,

            main_kpis_req: '11k',
            main_kpis_success: '11%',
            main_kpis_bw: '51Mb',
            main_kpis_confs: '4',

            modal_zoom_req: null,

            selectedFilterConfig: 0,
            optionsFilterConfig: [
                { value: 0, text: 'ALL : Select a config to filter on' }
            ],


            config_stats_table : {
                perPage: 10,
                currentPage: 1,
                fields: [ 'id', { key: "name", tdClass: "tdBreakWords" }, { key: "proxy", tdClass: "tdBreakWords" }, 'bandwidth' , 'requests' , 'success' , 'edit', 'del' ],
                items: [

                ],
            },

            sites_stats_table : {
                perPage: 10,
                currentPage: 1,
                fields: [ 'regex', 'site_hex' , 'created_at' , 'bandwidth' , 'requests' , { key: "bl_rate", label: 'BL. rate' } , 'edit', 'del' ],
                items: [

                ],
            },

            sites_configs_stats_table : {
                perPage: 10,
                currentPage: 1,
                fields: [ 'regex', 'config_id' , 'config_name' , 'bandwidth' , 'requests' , { key: "bl_rate", label: 'BL. rate' } ],
                items: [
                    
                ],
            },

            protocol_protocol_table: {
                perPage: 3,
                currentPage: 1,
                fields: [ 'protocol', 'bandwidth' , 'requests' , 'success' ],
                items: [

                ],
            },

            domain_protocol_table: {
                perPage: 8,
                currentPage: 1,
                fields: [ { key: "domain", tdClass: "tdBreakWords" }, 'bandwidth' , 'requests' , 'success' ],
                items: [

                ],
            },

            last_requests_table: {
                perPage: 20,
                currentPage: 1,
                fields: ["domain", { key: "url", tdClass: "tdBreakWords" }, 'config', 'protocol' ,'status' , 'bandwidth' , { key: "time", label: "Time (ms)" }, { key: "time_internet", label: "Req Time (ms)" }, 'date' ,'details' ],
                items: [
                    
                ],
            },
            
            conf_flagged_for_del : null,
            site_flagged_for_del: null,

            configNewName: '',
            configNewNameState: null,

            siteNewRegex: '',
            siteNewRegexState: null,
        }),
        mounted: function(){
            this.reload_page(true);
        },

        methods: {
            reload_page: function(coldstart){
                let this_obj = this;
                this_obj.$parent.switchHeaderLoadingIcon(true);

                if (coldstart == true){
                    this_obj.loading_main = true;
                }

                this.$store.axios_obj.get('/summary/'+String(this_obj.selectedFilterConfig),{
                    headers: {
                        'Authorization': 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                    }
                })
                .then(response =>{
                    if (response === null){
                        this_obj.$toasted.error('Error during refresh ! Empty server reponse').goAway(5000);
                        return;
                    }

                    if (response.status === 200){
                        let select_options = [{ value: 0, text: 'ALL : Select a config to filter on' }];

                        for (var i = 0; i < response.data.configs_stats.length; i++) {
                            let node_id = response.data.configs_stats[response.data.configs_stats.length - 1 - i];
                            select_options.push({ value: parseInt(node_id['id']), text: node_id['id'] + ' : ' + node_id['name'] });
                        }
                        this_obj.optionsFilterConfig = select_options;

                        this_obj.config_stats_table.items = response.data.configs_stats;
                        this_obj.protocol_protocol_table.items = response.data.stats_by_protocol;
                        this_obj.domain_protocol_table.items = response.data.stats_by_domain;
                        this_obj.last_requests_table.items = response.data.req_logger;
                        

                        this_obj.main_kpis_req = response.data.global_kpis.requests;
                        this_obj.main_kpis_success = response.data.global_kpis.success;
                        this_obj.main_kpis_bw = response.data.global_kpis.bandwidth;
                        this_obj.main_kpis_confs = response.data.global_kpis.configs;

                        this_obj.sites_stats_table.items = response.data.sites; 
                        this_obj.sites_configs_stats_table.items = response.data.sites_cross_confs; 

                        

                        if (coldstart == true){
                            this_obj.loading_main = false;
                        }else{
                            this_obj.$toasted.success('Refreshed').goAway(1000);
                        }
                        this_obj.$parent.switchHeaderLoadingIcon(false);
                    }else{
                        this_obj.$toasted.error('Error during refresh ! code: ' + String(response.status)).goAway(5000);
                    } 

                    return;
                    
                })
                .catch(error =>{
                    this_obj.$toasted.error('Error during refresh ! error : ' + String(error)).goAway(5000);
                    return;
                })
            },
            closeModal: function(ref){
                this.$refs[ref].hide();
            },

            delete_config: function(id_config){
                this.conf_flagged_for_del = id_config;
                this.$refs['modal_config_delete'].show();
            },

            delete_site: function(site_hex){
                this.site_flagged_for_del = site_hex;
                this.$refs['modal_site_delete'].show();
            },

            _delete_site_confirm: function(){
                let site_hex_to_del = this.site_flagged_for_del;

                let this_obj = this;
                this.$store.axios_obj.post('/sites/delete' ,{"site_hex": site_hex_to_del},{
                    headers: {
                        Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                    }
                })
                .then(response =>{
                    if (response === null){
                        this_obj.$toasted.error('Error during Site deletion ! Empty server reponse').goAway(5000);
                        return;
                    }

                    if (response.status === 200){
                        this_obj.$toasted.success('Site deleted !').goAway(1000);
                        this_obj.reload_page(false);
                    }else{
                        this_obj.$toasted.error('Error during Site deletion ! code: ' + String(response.status)).goAway(5000);
                    }

                    return;
                })
                .catch(error =>{
                    this_obj.$toasted.error('Error during Site deletion ! error : ' + String(error)).goAway(5000);
                    return;
                });
            },

            _delete_config_confirm: function(){
                let id_config = this.conf_flagged_for_del;

                let this_obj = this;
                this.$store.axios_obj.get('/configs/delete/' + String(id_config),{
                    headers: {
                        Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                    }
                })
                .then(response =>{
                    if (response === null){
                        this_obj.$toasted.error('Error during Config deletion ! Empty server reponse').goAway(5000);
                        return;
                    }

                    if (response.status === 200){
                        this_obj.$toasted.success('Config deleted !').goAway(1000);
                        this_obj.reload_page(false);
                    }else{
                        this_obj.$toasted.error('Error during Config deletion ! code: ' + String(response.status)).goAway(5000);
                    }

                    return;
                })
                .catch(error =>{
                    this_obj.$toasted.error('Error during Config deletion ! error : ' + String(error)).goAway(5000);
                    return;
                });
            },

            more_details_req: function(req_node){
                const bson_converter_lib_obj = new bson_converter_lib();
                this.modal_zoom_req = bson_converter_lib_obj.decode_json(req_node).details_node;
                this.$refs['bv_modal_show_req'].show();
            },

            new_config: function(){
                this.configNewName = '';
                this.$refs['modal_new_config'].show();
            },

            new_site: function(){
                this.siteNewRegex = '';
                this.$refs['modal_new_site'].show();
            },

            storeNewConfig: function(){
                if (String(this.configNewName) == ""){
                    this.$toasted.error('Please specify a config name !').goAway(5000);
                }else{
                    let payload_new_config_empty = {};
                    payload_new_config_empty['config_name'] = String(this.configNewName);

                    payload_new_config_empty['do_not_modify_connection_header'] = false;
                    

                    payload_new_config_empty['ssl'] = {};
                    payload_new_config_empty['ssl']['verify_ssl'] = false;
                    payload_new_config_empty['ssl']['version'] = 'PROTOCOL_TLS';
                    
                    let this_obj = this;
                    this.$store.axios_obj.post('/configs/new',{'config':payload_new_config_empty}, {
                        headers: {
                            Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                        }
                    })
                    .then(response =>{
                        if (response === null){
                            this_obj.$toasted.error('Error during Config creation ! Empty server reponse').goAway(5000);
                            return;
                        }

                        if (response.status === 200){
                            this_obj.$toasted.success('Config created !').goAway(1000);
                            this_obj.reload_page(false);
                        }else{
                            this_obj.$toasted.error('Error during Config creation ! code: ' + String(response.status)).goAway(5000);
                        }

                        return;
                    })
                    .catch(error =>{
                        this_obj.$toasted.error('Error during Config creation ! error : ' + String(error)).goAway(5000);
                        return;
                    });
                }
            },

            storeNewSite: function(){
                if (String(this.siteNewRegex) == ""){
                    this.$toasted.error('Please specify a Site regex identifier !').goAway(5000);
                }else{
                    let payload_new_site_empty = {};
                    payload_new_site_empty['regex'] = String(this.siteNewRegex);
                    payload_new_site_empty['blacklist_detection'] = '';
                    
                    let this_obj = this;
                    this.$store.axios_obj.post('/sites/new',{'site':payload_new_site_empty}, {
                        headers: {
                            Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                        }
                    })
                    .then(response =>{
                        if (response === null){
                            this_obj.$toasted.error('Error during Site creation ! Empty server reponse').goAway(5000);
                            return;
                        }

                        if (response.status === 200){
                            this_obj.$toasted.success('Site created !').goAway(1000);
                            this_obj.reload_page(false);
                        }else{
                            this_obj.$toasted.error('Error during Site creation ! code: ' + String(response.status)).goAway(5000);
                        }

                        return;
                    })
                    .catch(error =>{
                        this_obj.$toasted.error('Error during Site creation ! error : ' + String(error)).goAway(5000);
                        return;
                    });
                }
            },

            _flush_cache_confirm: function(){
                let this_obj = this;
                this.$store.axios_obj.get('/logs/flush_redis', {
                    headers: {
                        Authorization: 'Basic ' + btoa(this.$store.getters.fetchStoredToken + ':' )
                    }
                })
                .then(response =>{
                    if (response === null){
                        this_obj.$toasted.error('Error during Stats Flush ! Empty server reponse').goAway(5000);
                        return;
                    }

                    if (response.status === 200){
                        this_obj.$toasted.success('Stats flused !').goAway(1000);
                        this_obj.reload_page(false);
                    }else{
                        this_obj.$toasted.error('Error during Stats Flush ! code: ' + String(response.status)).goAway(5000);
                    }

                    return;
                })
                .catch(error =>{
                    this_obj.$toasted.error('Error during Stats Flush ! error : ' + String(error)).goAway(5000);
                    return;
                });
            }
        },

        computed: {
            config_stats_table_rows() {
                return this.config_stats_table.items.length
            },

            last_requests_table_rows(){
                return this.last_requests_table.items.length
            },

            sites_stats_table_rows(){
                return this.sites_stats_table.items.length;
            },

            sites_configs_stats_table_rows(){
                return this.sites_configs_stats_table.length;
            }
        }
    }


</script>
<style>
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