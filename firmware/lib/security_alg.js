$(function(){

    var AlgInfo = Backbone.Model.extend({
        validate:function(attrs) {

        }
    });


    var AlgInfoList = Backbone.Collection.extend({
        model : AlgInfo,
        url : "/1/Device/Firewall/ALG",
        postUrl : "/1/Device/Firewall/ALG",
        initialize : function(){

        }
    });


    var algInfoList = new AlgInfoList();

    var AlgInfoView = Backbone.View.extend({
        el: $("#algDiv"),
        template : _.template($("#alg-template").html()),
        events: {
            "click .btn-disabled" : "toggle"
        },
        initialize : function(){
            this.model.bind("change", this.render, this);
        },
        render: function(){
            $("#algDiv").html(this.template(this.model.toJSON()));
			if(this.model.get("Conntrack_ALGSipOnOff") == "Disabled")
			{
			    $("#algSipOn").addClass("disabled");
				$("#algSipOn").attr("disabled","disabled");
				this.model.set("ALGSipOnOff","Disabled");
			}
			if(this.model.get("ALGSipOnOff") == "Enabled")
			{
			    $("#conntrack_algSipOff").addClass("disabled");
				$("#conntrack_algSipOff").attr("disabled","disabled");
			}

            return this;
        },
        toggle: function(event){
            var attrName = $(event.currentTarget).attr("name");
            var attrId = $(event.currentTarget).attr("id");
            var attrValue = $(event.currentTarget).val();
            this.model.set(attrName,attrValue);
			if (attrName == "Conntrack_ALGSipOnOff")
			{
				if(attrValue == "Disabled")
				{
					$("#algSipOn").addClass("disabled");
					$("#algSipOn").attr("disabled","disabled");
					this.model.set("ALGSipOnOff","Disabled");
				}
				else
				{
					$("#algSipOn").removeClass("disabled");
					$("#algSipOn").removeAttr("disabled");
				}
			}
			if (attrName == "ALGSipOnOff")
			{
				if(attrValue == "Enabled")
				{
					$("#conntrack_algSipOff").addClass("disabled");
					$("#conntrack_algSipOff").attr("disabled","disabled");
				}
				else
				{
					$("#conntrack_algSipOff").removeClass("disabled");
					$("#conntrack_algSipOff").removeAttr("disabled");
				}
			}

				this.model.save({"_method": "PUT"},{
                success:function(){
                    $('#btnApply').button('reset');
                    $('#alertType').text('[Success]');
                    $('#alertInfo').text($.tag_get("WarnMsg_Saved_1"));
                    /*if(attrName == "ALGOnOff")
                        $('#alertInfo').text($.tag_get("WarnMsg_Saved_1") +
                                             $.tag_get("Basic_Setting_GatewayFunc_Warning_3"));*/
                    $('#alertArea').attr('class','alert alert-success');
                    $('#alertArea').fadeIn();
					$('#alertArea').fadeOut(2000);
					}
            });
				}
	});

    var algMainView = Backbone.View.extend({
        el : $("#algMain"),
        alertAres: $("#alertArea"),
        events:{
            "click #btnCloseAlert":"closeAlert"
        },
        initialize : function(){
            algInfoList.bind("reset", this.renderAlg, this);
            algInfoList.fetch();
        },
        renderAlg: function(){
            algInfoList.each(function(alg){
            var algView = new AlgInfoView({model:alg});
            algView.render();
            alg.on("error",function(model,error){
                $('#alertArea').attr('class','alert alert-error');
                $('#alertType').text('[ERROR]');
                $('#alertInfo').text(error);
                $('#alertArea').fadeIn();
                });
            });
        },
        closeAlert:function() {
            $('#alertArea').fadeOut();
        }
    });

    var mainView = new algMainView();
    $.hitron.languages.lang_load();
});
