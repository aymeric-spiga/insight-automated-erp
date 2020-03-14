#!/usr/bin/env bash
#----------------------------------------------------------------------------------------------------------------------#
# Script d'exemple pour l'envois d'ERP à l'API du SISMOC à partir d'un fichier XML
#
#     Dépendances:
#        * curl - requêtes HTTP à l'API du SISMOC
#        * zip  - créer l'archive
#
#      Testé sur:
#        * Ubuntu 18
#
#      Doc de l'API SISMOC:
#        * https://ebm-sismoc-preprod.cnes.fr/ebm-rest-server/assets/api-doc/
#
#      PHONE OF SISMOC: +33 (0)5 61 28 28 82
#
#----------------------------------------------------------------------------------------------------------------------#

# Strict mode
set -euo pipefail
IFS=$'\n\t'

#
# 0 - Constantes et variables
#
#     Le jeton et le chemin ver le xml pourraient être passés comme arguments du scrispt
#
# PREPROD SERVER TO DE TESTED THERE BEFORE
SISMOC_REST_SERVER_URL='https://ebm-sismoc-preprod.cnes.fr/ebm-rest-server'
#
# PRODUCTION SERVER !!! ONLY ONCE THE CODE IS FULLY VALIDATED !!!
#SISMOC_REST_SERVER_URL='https://ebm-sismoc.cnes.fr/ebm-rest-server'

xml_files=`ls *.xml`
xml_save_path='./ERP_xml'
echo $xml_files

# Put there your login password, 
# or use the code below if you do not want to hard code login and password
username=""
pwd=""
# Other option to avoid hard coding the login pasword (not tested by RF Garcia)
#if [ -z "$1" ]; then
#read -p "username ? " rep
#username=$rep
#else
#username=${1}
#fi
#
#if [ -z "$2" ]; then
#read -s -p "password ? " repp
#pass=$repp
#else
#pass=${2}
#fi

# get auth_token
auth_token=`curl -sS -f -X POST "${SISMOC_REST_SERVER_URL}/auth"  -H "Content-Type: application/json"  -d "{\"username\":\"${username}\", \"password\":\"${pwd}\"}"  | jq -r '.jwt'`
echo $auth_token

# loop over all ERP xml files in the current directory
for file in $xml_files; do
echo $file
zip_archive_path="${file%.*}.zip"
echo ${zip_archive_path}
rm -Rf ${zip_archive_path}
zip ${zip_archive_path} $file 

#
# 2 - Validation de l'ERP auprès de SISMOC
#
#     L'option --fail de curl va faire planter le script si la réponse de SISMOC est 4xx ou 5xx
#     L'option --show-error fait que curl écrit l'erreur et assure que les 401 sont bien considérées comme un fail
#

curl --fail --silent --show-error --output /dev/null \
    -X POST "${SISMOC_REST_SERVER_URL}/erps?validateOnly=true" \
    -H "Authorization: Bearer ${auth_token}" \
    -F "ERP=@./${zip_archive_path}"
#    -F "ERP=@$file"

#
# 3 - Envoi de l'ERP au SISMOC
#
#     On peut imaginer rediriger la sortie standard dans un fichier ayant
#     le même nom que le fichier xml pour faire office de rapport ?
#     > ${xml_file_path/xml/sismoc.response.json}
#
curl --show-error --fail \
    -X POST "${SISMOC_REST_SERVER_URL}/erps" \
    -H "Authorization: Bearer ${auth_token}" \
    -F "ERP=@./${zip_archive_path}"
#    -F "ERP=@$file"

rm -Rf ${zip_archive_path}
# move the ERP into the storage directory of ERPs
mv $file ${xml_save_path}

done

exit 0
