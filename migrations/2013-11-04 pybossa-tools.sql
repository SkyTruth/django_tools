alter table appomatic_pybossa_tools_app add column "server_id" integer NOT NULL REFERENCES "appomatic_pybossa_tools_server" ("id") DEFERRABLE INITIALLY DEFERRED;
alter table appomatic_pybossa_tools_app drop column appid;
