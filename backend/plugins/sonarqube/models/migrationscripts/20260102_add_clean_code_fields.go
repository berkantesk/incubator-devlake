/*
Licensed to the Apache Software Foundation (ASF) under one or more
contributor license agreements.  See the NOTICE file distributed with
this work for additional information regarding copyright ownership.
The ASF licenses this file to You under the Apache License, Version 2.0
(the "License"); you may not use this file except in compliance with
the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package migrationscripts

import (
	"github.com/apache/incubator-devlake/core/context"
	"github.com/apache/incubator-devlake/core/errors"
	"github.com/apache/incubator-devlake/core/plugin"
)

var _ plugin.MigrationScript = (*addCleanCodeFields)(nil)

type addCleanCodeFields struct{}

func (script *addCleanCodeFields) Up(basicRes context.BasicRes) errors.Error {
	db := basicRes.GetDal()
	// Add SonarQube 10 Clean Code taxonomy fields to issues table
	err := db.AddColumn("_tool_sonarqube_issues", "clean_code_attribute", "varchar(100)")
	if err != nil {
		return err
	}
	return db.AddColumn("_tool_sonarqube_issues", "clean_code_attribute_category", "varchar(100)")
}

func (*addCleanCodeFields) Version() uint64 {
	return 20260102000000
}

func (*addCleanCodeFields) Name() string {
	return "add clean code fields for SonarQube 10"
}
