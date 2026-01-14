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

package tasks

import (
	"net/http"

	"github.com/apache/incubator-devlake/core/errors"
	"github.com/apache/incubator-devlake/core/plugin"
	"github.com/apache/incubator-devlake/helpers/pluginhelper/api"
	"github.com/apache/incubator-devlake/plugins/sonarqube/models"
)

// CreateApiClient creates a new asynchronize API Client for AE
func CreateApiClient(taskCtx plugin.TaskContext, connection *models.SonarqubeConnection) (*api.ApiAsyncClient, errors.Error) {
	apiClient, err := api.NewApiClientFromConnection(taskCtx.GetContext(), taskCtx, connection)
	if err != nil {
		return nil, err
	}

	// create ae api client
	asyncApiCLient, err := api.CreateAsyncApiClient(taskCtx, apiClient, nil)
	if err != nil {
		return nil, err
	}

	return asyncApiCLient, nil
}

// ignoreHTTPStatus403 ignores 403 Forbidden errors which occur when the access token
// doesn't have sufficient permissions (e.g., Browse permission for file metrics).
// This allows the pipeline to continue collecting other data instead of failing entirely.
func ignoreHTTPStatus403(res *http.Response) errors.Error {
	if res.StatusCode == http.StatusUnauthorized {
		return errors.Unauthorized.New("authentication failed, please check your AccessToken")
	}
	if res.StatusCode == http.StatusForbidden {
		return api.ErrIgnoreAndContinue
	}
	return nil
}
