# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class tortuga::installer::basic {
  include tortuga::config

  file { '/etc/tortuga-release':
    ensure => symlink,
    target => "${tortuga::config::instroot}/etc/tortuga-release",
  }

  file { '/etc/logrotate.d/tortugawsd':
    source => "file://${tortuga::config::instroot}/etc/tortugawsd.logrotate",
  }

  file { '/etc/logrotate.d/celery':
    source => "file://${tortuga::config::instroot}/etc/celery.logrotate",
  }

}
