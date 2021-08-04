export default class bson_converter {
    constructor() {
        
    }
    _decode_json_recursively(input_json){
        for (var k in input_json) {
            if (typeof input_json[k] == "object" && input_json[k] !== null){
                input_json[k] = this._decode_json_recursively(JSON.parse(JSON.stringify(input_json[k] )));
            }else{
                if ((k === "$binary") && ("$type" in input_json) && (input_json["$type"] === "00")){
                    input_json = atob(input_json[k]);
                }else{
                    // do not touch !
                }
            }
        }
        return input_json;
    }

    decode_json(input_json){
        var copy_input_json = JSON.parse(JSON.stringify(input_json));
        return this._decode_json_recursively(copy_input_json);
    }
}
