define (require, exports) ->

    exports.Validators =
        is_array: (x) ->
            return Array.isArray(x) if Array.isArray
            Object.prototype.toString.call(x) == "[object Array]"
        
        is_string: (x) ->
            Object.prototype.toString.call(x) == "[object String]"

        is_number: (x) ->
            return true if Object.prototype.toString.call(x) == "[object Number]"

            if @is_string x
                regex = /^\-?[0-9]*\.?[0-9]+$/
                return regex.test x

            false

        is_function: (x) -> 
            Object.prototype.toString.call(x) == "[object Function]"

        is_object: (x) ->
            return false if Object.prototype.toString.call(x) != "[object Object]"

            for key of x
                break

            !key or Object.prototype.hasOwnProperty.call(x, key)

        is_email: (x) ->
            if @is_string x
                regex = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$/i
                return regex.test x
            false

        is_empty: (x) ->
            x = x.toString() if false == @is_string x
        
            return true if x == null 
            return true if exports.Filters.trim(x) == "" 
            false

        is_url: (x) ->
            /((http|https):\/\/(\w+:{0,1}\w*@)?(\S+)|)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/.test(x)

        is_ip: (x) ->
            octet = '(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])';
            ip    = '(?:' + octet + '\\.){3}' + octet;
            quad  = '(?:\\[' + ip + '\\])|(?:' + ip + ')';
            regex = new RegExp( '(' + quad + ')' );
            regex.test x

        is_whitespace: (x) ->
            x = x.toString() if false == @is_string x
            regex = /^\s*$/
            regex.test(x)

            

    exports.Filters =
        trim: (x) ->
            x = x.toString() if false == exports.Validators.is_string x
            return x.trim() if String.prototype.trim

            if exports.Validators.is_whitespace "\xA0"
                trim_left  = /^\s+/
                trim_right = /\s+$/
            else
                trim_left  = /^[\s\xA0]+/
                trim_right = /[\s\xA0]+$/

            x.replace(trim_left, "").replace(trim_right, "")

        ucfirst: (x) ->
            return String(x).replace(/\b\w+\b/, (word) ->
               return word.substring(0,1).toUpperCase() + word.substring(1)
            )

        to_text: (x) ->
            String(x).replace(/<[^>].*?>/g,"")

        to_number: (x) ->
            return Number x if exports.Validators.is_number x
            0

    return

