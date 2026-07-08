var checkConnInterval;
var SessionTimeout = 10 * 60; /*default*/
var SessionRemain = 10 * 60; /*default*/
var SessionResetFlag = 0;
var SessionInterval;
var currentUser = "";
var wpsInterval;
var modelName = "";

$(function () {
    ///Define the menus
    //The definition of Menu model.
    var Menu = Backbone.Model.extend({
        // Default attributes for the todo item.
        defaults: function () {
            return {
                tagName: "Tag",
                langTagId: "menu_tag",
                hyperLink: "#",
                visible: false,
                selected: false
            };
        },
        // If tag name is not defined, set the menu to default.
        initialize: function () {
            if (!this.get("tagName")) {
                this.set(this.defaults());
            }
            if (!this.get("selected")) {
                this.set({ "selected": this.defaults().selected });
            }
        }
    });

    //Define the menu collection.
    var MenuList = Backbone.Collection.extend({
        model: Menu,
        url: "/1/Device/Menu/Main",
        postUrl: "/1/Device/Menu/Main",
        listName: "MenuList",
        // Only one menu in the menulist can be selected.
        select: function (index) {
            for (i = 0; i < this.length; i++) {
                if (this.models[i].get("index") == index)
                    this.models[i].set("selected", true);
                else
                    this.models[i].set("selected", false);
            }
        }
    });

    //submenu: extend top menu collection.
    var SubMenuList = MenuList.extend({
        url: "/1/Device/Menu/Sub",
        postUrl: "/1/Device/Menu/Sub",
        listName: "SubMenuList"
    });

    var menus = new MenuList;
    var subMenus = new SubMenuList;

    //Define menu view
    var MenuView = Backbone.View.extend({
        tagName: "li",
        template: _.template($("#menuitem-template").html()),
        events: {
            "click": "selectMenu"
        },
        initialize: function () {
            this.model.bind("change", this.render, this);
        },
        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            if (this.model.get("selected"))
                this.$el.attr("class", "active");
            else
                this.$el.removeAttr("class");

            if (this.model.get("visible") == false)
                this.$el.hide();
            return this;
        },
        selectMenu: function () {
        }
    });

    //Submenu view
    var SubMenuView = Backbone.View.extend({
        tagName: "li",
        template: _.template($("#submenu-template").html()),
        events: {
            "click": "selectMenu",
            "dblclick": "selectMenu"
        },
        initialize: function () {
            this.model.bind("reset", this.render, this);
            this.model.bind("change", this.render, this);
        },
        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            if (this.model.get("selected"))
                this.$el.attr("class", "active");
            else
                this.$el.removeAttr("class");

            if (this.model.get("visible") == false)
                this.$el.hide();
            return this;
        },
        selectMenu: function () {
        }
    });

    //Define the head view.
    var HeadView = Backbone.View.extend({
        el: $("#menuTitle"),
        template: _.template($("#head-template").html()),
        submenuTemplate: _.template($("#submenu-template").html()),
        initialize: function () {
            this.model.bind("change", this.render, this);
            subMenus.bind("reset", this.showSubMenus, this);
            if (this.model.get("selected"))
                subMenus.fetch();
        },
        render: function () {
            if (this.model.get("selected"))
                $("#menuTitle").html(this.template(this.model.toJSON()));

            return this;
        },
        showSubMenus: function () {
            if (this.model.get("selected")) {
                $("#submenus").html("");
                var mainMenuId = this.model.get("index");
                var loadUrl;

                subMenus.each(function (menu) {
                    var submenuview = new SubMenuView({ model: menu });
                    this.$("#submenus").append(submenuview.render().el);
                    if (menu.get("selected"))
                        loadUrl = menu.get("hyperLink");
                });

                $("#maincontent").fadeOut("fast", function () {
                    $("#maincontent").html("");
                    setCookie("isEdit", "0", 24 * 30, "/");
                    setCookie("isEdit1", "0", 24 * 30, "/");
                    setCookie("isEdit2", "0", 24 * 30, "/");
                    setCookie("isEdit3", "0", 24 * 30, "/");
                    $("#maincontent").load(loadUrl + ".html");
                    $("#maincontent").fadeIn();
                });
            }
        }
    });

    var AppView = Backbone.View.extend({
        // Instead of generating a new element, bind to the existing skeleton of
        // the App already present in the HTML.
        el: $("#mainApp"),
        events: {
            "click #btnLogout": "logOut",
            "click .langSelect": "setLanguage",
            "change #selLanguage": "setLanguage"
        },
        initialize: function () {
            $.getJSON("/1/Device/CM/Version?_=" + Math.random(), function (json) {
                modelName = json.modelName;
                document.title = json.modelName + " " + $.tag_get("Menu_Title");
                if ($.hitron.isChita()) {
                    $.hitron.addCssForChita(json);
                    //$("#mainIndex").remove();
                }
                else {
                    //$("#mainIndex_chita").remove();
                }
                if (!$.hitron.isChita()) {
                    if ($.hitron.languages.lang_current == "fr_CA")
                        $("#currentLanguage").html($.tag_get("French"));
                    else
                        $("#currentLanguage").html("English");

                    var date, year;
                    date = new Date();
                    year = date.getFullYear();
                    $("#copyright").html("&copy; " + year + " " + $.tag_get("Copyright"));
                }
            });

            menus.bind("reset", this.showMenus, this);
            //Backbone.history.start();
            menus.fetch();
            setCookie("isEdit", "0", 24 * 30, "/");
            setCookie("isEdit1", "0", 24 * 30, "/");
            setCookie("isEdit2", "0", 24 * 30, "/");
            setCookie("isEdit3", "0", 24 * 30, "/");

            $.getJSON("/1/Device/Users/CSRF?_=" + Math.random(), function (json) {
                if (json.CSRF != "")
                    $("#csrf_token").val(json.CSRF);
            });
            $.get("/1/Device/Users/Name?_=" + Math.random(), function (data) {
                data = $.parseJSON(data);
                var name = data.Name;
                //console.log(data.Name);
                var num = $("#currentUser").attr("limit");
                $("#titleid").attr("title", name);
                if (name.length > num)
                    name = name.substring(0, num) + "...";
                $("#currentUser").html(name);
            });

            $("#mainApp").fadeIn("slow");
        },
        showMenus: function () {
            $("#topMenu").html("");
            menus.each(function (menu) {
                var menuview = new MenuView({ model: menu });
                this.$("#topMenu").append(menuview.render().el);
                var headview = new HeadView({ model: menu });
                //Render the head view.includeing tiltes and submenus.
                if (menu.get("selected")) {
                    headview.render();
                }
            });
        },
        logOut: function () {
            this.$el.fadeOut(function () {
                $.post("/1/Device/Users/Logout", function () {
                    window.location = "login.html";
                })
                .fail(function () {
                    window.location = "login.html";
                });
            });
        },
        setLanguage: function (event) {
            $.hitron.languages.lang_set($(event.currentTarget).val());
        }
    });

    Backbone.emulateHTTP = true;
    Backbone.emulateJSON = true;
    $.ajaxSetup({ cache: false });

    ////Define the app router for history manage.
    var AppRouter = Backbone.Router.extend({
        routes: {
            ":loadUrl/m/:menuId/s/:subMenuId": "goPage"
        },
        goPage: function (loadUrl, menuId, subMenuId) {
            var i;
            if (getCookieValue("isEdit") != "0" || getCookieValue("isEdit1") != "0" || getCookieValue("isEdit2") != "0" || getCookieValue("isEdit3") != "0") {
                if (!confirm($.tag_get("Info_Leave_Confirm"))) {
                    window.location.hash += "/1";
                    return;
                }
            }
            clearInterval(wpsInterval);
            if (menus.length == 0) {
                /* users input url or reload the page */
                return;
            }
            /* get the new url menuId index */
            for (i = 0; i < menus.length; i++) {
                if (menus.models[i].get("index") == menuId)
                    break;
            }
            /* get the old url menuId index */
            if (menus.models[i].get("selected") == false) {
                /* menu has changed, need to fetch submenu */
                menus.select(menuId);
                $("a").bind("click", function (event) {
                    event.preventDefault();
                });
                menus.models[i].save({ "index": menuId, "subIndex": subMenuId }, {
                    success: function () {
                        subMenus.fetch({
                            success: function () {
                                $("a").unbind("click");
                                setCookie("isEdit", "0", 24 * 30, "/");
                                setCookie("isEdit1", "0", 24 * 30, "/");
                                setCookie("isEdit2", "0", 24 * 30, "/");
                                setCookie("isEdit3", "0", 24 * 30, "/");
                            }
                        });
                    }
                });
            }
            else {
                /* Only submenu changed */
                for (i = 0; i < subMenus.length; i++) {
                    if (subMenus.models[i].get("index") == subMenuId)
                        break;
                }
                subMenus.select(subMenuId);
                $("a").bind("click", function (event) {
                    event.preventDefault();
                });
                subMenus.models[i].save({ "index": subMenuId, "mainIndex": menuId, "loadurl": loadUrl }, {
                    success: function () {
                        $("#maincontent").fadeOut("fast", function () {
                            $("#maincontent").html("");
                            setCookie("isEdit", "0", 24 * 30, "/");
                            setCookie("isEdit1", "0", 24 * 30, "/");
                            setCookie("isEdit2", "0", 24 * 30, "/");
                            setCookie("isEdit3", "0", 24 * 30, "/");
                            $("#maincontent").load(loadUrl + ".html", function (response, status) {
                                if (status == "success")
                                    $("a").unbind("click");
                            });
                            $("#maincontent").fadeIn();
                        });
                    },
                    error: function () {
                    }
                });
            }
        }
    });

    $.hitron.languages.lang_init();
    $("#selLanguage").val($.hitron.languages.lang_current);
    var App = new AppView;
    approuter = new AppRouter;
    Backbone.history.start();

    window.onbeforeunload = function () {
        if (SessionRemain <= 0) {
            return;
        }
        if (getCookieValue("isEdit") != "0" || getCookieValue("isEdit1") != "0" || getCookieValue("isEdit2") != "0" || getCookieValue("isEdit3") != "0") {
            return $.tag_get("Info_Leave_Confirm");
        }
        return;
    }

    $.get("/1/Device/Users/Manage?_=" + Math.random(), function (data) {
        data = $.parseJSON(data);
        SessionTimeout = data.Users_list[0].idleTime;
        SessionRemain = SessionTimeout;
        SessionInterval = setInterval(SessionFn, 1000);
    });

    var SessionFn = function () {
        if (SessionResetFlag == 1) {
            SessionRemain = SessionTimeout;
            SessionResetFlag = 0;
        }
        SessionRemain -= 1;
        if (SessionRemain <= 0) {
            clearInterval(SessionInterval);
            window.location = "login.html";
        }
    };

    var checkConnFn = function() {
        $.ajax({
            type: "get",
            async: false,
            url: "/1/Device/Users/Alive?_=" + Math.random(),
            cache: false,
            timeout: 10000,
            success: function(result) {
            },
            error: function() {
                clearInterval(checkConnInterval);
                if (confirm($.tag_get("Info_Connect_Failed_Confirm"))) {
                    if (SessionRemain >= 0){
                        clearInterval(SessionInterval);
                    }
                    window.location = "/";
                }
            }
        });
    };

    checkConnInterval = setInterval(checkConnFn, 60000);
});

